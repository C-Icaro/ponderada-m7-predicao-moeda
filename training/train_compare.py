"""Treina primeiro três anos e depois o histórico longo, com avaliação temporal."""

import hashlib
import importlib.metadata
import json
import platform
import shutil
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from prophet import Prophet
from prophet.serialize import model_from_json, model_to_json

VALIDATION_START = pd.Timestamp("2026-04-08")
TEST_START = pd.Timestamp("2026-07-07")
END_EXCLUSIVE = pd.Timestamp("2026-10-05")
SEED = 42
PARAMETERS = {
    "growth": "linear", "yearly_seasonality": True, "weekly_seasonality": True,
    "daily_seasonality": False, "n_changepoints": 25, "changepoint_range": 0.8,
    "changepoint_prior_scale": 0.05, "seasonality_mode": "additive",
    "seasonality_prior_scale": 10.0, "mcmc_samples": 0, "uncertainty_samples": 0,
}
WINDOWS = {
    "3y": ("data/processed/btc_usd_daily.csv", "data/coleta-btc-usd.json"),
    "12y": ("data/processed/btc_usd_daily_12y.csv", "data/coleta-btc-usd-12y.json"),
}


def metrics(actual, predicted):
    actual, predicted = np.asarray(actual, dtype=float), np.asarray(predicted, dtype=float)
    if actual.shape != predicted.shape or not actual.size:
        raise ValueError("Métricas precisam de observações e previsões com o mesmo tamanho.")
    if not np.isfinite(actual).all() or not np.isfinite(predicted).all():
        raise ValueError("Métricas não aceitam valores ausentes ou infinitos.")
    error = np.abs(actual - predicted)
    denominator = np.abs(actual) + np.abs(predicted)
    smape = np.divide(200 * error, denominator, out=np.zeros_like(error), where=denominator != 0)
    return {"mae_usd": float(error.mean()), "rmse_usd": float(np.sqrt((error ** 2).mean())),
            "smape_percent": float(smape.mean())}


def load_data(root, csv_path, metadata_path):
    path = root / csv_path
    provenance = json.loads((root / metadata_path).read_text(encoding="utf-8"))
    sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha256 != provenance["csv_sha256"]:
        raise ValueError(f"Hash diferente da procedência: {csv_path}")
    frame = pd.read_csv(path, parse_dates=["ds"])
    if list(frame.columns) != ["ds", "y"] or frame.empty:
        raise ValueError(f"CSV precisa conter apenas ds e y: {csv_path}")
    frame = frame.sort_values("ds").reset_index(drop=True)
    expected = list(pd.date_range(provenance["start_inclusive"], provenance["end_exclusive"],
                                  inclusive="left", freq="D"))
    if frame.ds.tolist() != expected or len(frame) != provenance["rows"]:
        raise ValueError(f"Datas incompletas ou duplicadas: {csv_path}")
    if frame.ds.dt.tz is not None or not np.isfinite(frame.y).all() or (frame.y <= 0).any():
        raise ValueError(f"Fuso ou preço incompatível: {csv_path}")
    return frame, {"csv_path": csv_path, "metadata_path": metadata_path,
                   "sha256": sha256, "bytes": path.stat().st_size, "rows": len(frame),
                   "first_date": frame.ds.iloc[0].date().isoformat(),
                   "last_date": frame.ds.iloc[-1].date().isoformat()}


def training_before(frame, cutoff):
    train = frame.loc[frame.ds < cutoff, ["ds", "y"]].copy()
    if train.empty or train.ds.max() >= cutoff:
        raise ValueError("O treino deve terminar antes do período previsto.")
    return train


def fit_model(train):
    started = perf_counter()
    model = Prophet(**PARAMETERS)
    model.fit(train, seed=SEED)
    return model, perf_counter() - started


def export_model(model, path, dates, original_predictions):
    path.write_text(model_to_json(model), encoding="utf-8")
    loaded = model_from_json(path.read_text(encoding="utf-8"))
    restored = loaded.predict(dates[["ds"]]).yhat.to_numpy()
    if not np.allclose(restored, original_predictions, rtol=1e-10, atol=1e-6):
        raise RuntimeError(f"A predição mudou após recarregar {path.name}.")
    return {"path": "models/" + path.name, "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "reload_max_abs_difference": float(np.max(np.abs(restored - original_predictions)))}


def evaluate_phase(root, frames, start, end, phase):
    observed = frames["3y"].loc[(frames["3y"].ds >= start) & (frames["3y"].ds < end)].copy()
    if observed.ds.tolist() != list(pd.date_range(start, end, inclusive="left", freq="D")):
        raise ValueError("Período de avaliação incompleto.")
    before = training_before(frames["3y"], start)
    baseline_predictions = np.full(len(observed), float(before.y.iloc[-1]))
    baseline = {**metrics(observed.y, baseline_predictions),
                "last_known_date": before.ds.iloc[-1].date().isoformat()}
    summary = {"start": start.date().isoformat(), "end": observed.ds.iloc[-1].date().isoformat(),
               "rows": len(observed), "horizon_days": len(observed),
               "baseline": baseline, "models": {}}
    predictions = observed[["ds", "y"]].reset_index(drop=True)
    predictions["baseline"] = baseline_predictions
    for window in ("3y", "12y"):
        train = training_before(frames[window], start)
        print(f"{phase}: ajustando {window}, {len(train)} registros até {train.ds.max().date()}", flush=True)
        model, seconds = fit_model(train)
        predicted = model.predict(observed[["ds"]]).yhat.to_numpy()
        predictions[window] = predicted
        item = {**metrics(observed.y, predicted), "train_rows": len(train),
                "train_start": train.ds.iloc[0].date().isoformat(),
                "train_end": train.ds.iloc[-1].date().isoformat(), "fit_seconds": seconds}
        if phase == "teste":
            item["artifact"] = export_model(model, root / "models" / f"modelo-{window}.json",
                                             observed, predicted)
        summary["models"][window] = item
    predictions.to_csv(root / "reports" / f"predicoes-{phase}.csv", index=False)
    return summary, predictions


def choose_window(validation):
    return min(("3y", "12y"), key=lambda window: (validation["models"][window]["mae_usd"],
                                                window != "3y"))


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                    encoding="utf-8")


def plot_test(root, predictions):
    fig, ax = plt.subplots(figsize=(11, 5))
    for column, label, color, style in [("y", "Observado", "#111827", "-"),
                                       ("3y", "Prophet: 3 anos", "#2563eb", "-"),
                                       ("12y", "Prophet: 12 anos", "#ea580c", "-"),
                                       ("baseline", "Último preço conhecido", "#6b7280", "--")]:
        ax.plot(predictions.ds, predictions[column], label=label, color=color, linestyle=style)
    ax.set(title="BTC-USD: teste de 90 dias, previsão feita no corte de 06/07/2026",
           ylabel="USD por BTC", xlabel="Data")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    for extension in ("png", "svg"):
        output = root / "reports" / f"comparacao-teste.{extension}"
        fig.savefig(output, dpi=150)
        if extension == "svg":
            output.write_text("\n".join(line.rstrip() for line in output.read_text(encoding="utf-8").splitlines())
                              + "\n", encoding="utf-8")
    plt.close(fig)


def format_number(value):
    return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def write_report(root, result):
    selected = result["selection"]["selected_window"]
    lines = ["# Comparação executada: três anos e histórico longo", "",
             "BTC-USD diário, fechamento em USD por BTC. Mesma configuração Prophet e semente 42.", "",
             "## Protocolo e resultado", "",
             "A validação vai de 08/04/2026 a 06/07/2026. O teste final vai de 07/07/2026 a 04/10/2026. "
             "Cada previsão cobre 90 dias a partir de um único corte, sem atualizações diárias.", "",
             "| Janela | MAE validação (USD) | MAE teste (USD) | RMSE teste (USD) | sMAPE teste |",
             "| --- | ---: | ---: | ---: | ---: |"]
    for window, label in [("3y", "3 anos"), ("12y", "Histórico longo, aproximadamente 12 anos")]:
        val, test = result["validation"]["models"][window], result["test"]["models"][window]
        lines.append(f"| {label} | {format_number(val['mae_usd'])} | {format_number(test['mae_usd'])} | "
                     f"{format_number(test['rmse_usd'])} | {format_number(test['smape_percent'])}% |")
    val, test = result["validation"]["baseline"], result["test"]["baseline"]
    lines.append(f"| Repetir último preço conhecido | {format_number(val['mae_usd'])} | "
                 f"{format_number(test['mae_usd'])} | {format_number(test['rmse_usd'])} | "
                 f"{format_number(test['smape_percent'])}% |")
    short_mae = result["test"]["models"]["3y"]["mae_usd"]
    long_mae = result["test"]["models"]["12y"]["mae_usd"]
    if short_mae == 0:
        difference_text = "O MAE de três anos foi zero; a diferença percentual não foi calculada."
    else:
        delta = 100 * (short_mae - long_mae) / short_mae
        direction = "menor" if delta >= 0 else "maior"
        difference_text = f"No teste, o MAE da janela longa foi {format_number(abs(delta))}% {direction} que o da janela de três anos."
    best_prophet_mae = min(short_mae, long_mae)
    if test["mae_usd"] < best_prophet_mae:
        baseline_text = ("A referência simples teve MAE de teste menor que os dois Prophet. Este experimento não comprova "
                         "vantagem de predição sobre repetir o último preço conhecido.")
    elif test["mae_usd"] > best_prophet_mae:
        baseline_text = "Pelo menos uma versão Prophet teve MAE de teste menor que a referência simples neste período."
    else:
        baseline_text = "A referência simples e a melhor versão Prophet empataram no MAE do teste."
    lines += ["", f"A janela selecionada exclusivamente pelo MAE de validação foi **{selected}**. "
              "Essa decisão foi gravada antes do cálculo do teste e não foi alterada pelo resultado final.", "",
              difference_text, "", baseline_text, "",
              "![Previsões e preços observados no teste](comparacao-teste.png)", "",
              "## Artefatos e limites", "",
              "Os modelos avaliados são `models/modelo-3y.json` e `models/modelo-12y.json`, ajustados até 06/07/2026. "
              "Os dois passaram pela verificação de previsão após exportar e recarregar JSON.", "",
              f"`models/modelo.json` foi reajustado usando a janela {selected} e dados até 04/10/2026. "
              "Esse ajuste final é destinado à futura integração e ainda não tem avaliação independente. "
              "Os modelos gerados e CSVs de predições ficam fora do Git; a reprodução está no código e no notebook.", "",
              "Uma única validação e um único teste não demonstram desempenho geral ou futuro. "
              "Não foram ajustados hiperparâmetros após observar o teste. Os intervalos de incerteza foram desabilitados.", "",
              "[Protocolo anterior à execução](../training/protocolo.md) · [Resultados completos e hashes](comparacao.json) · "
              "[Escolha registrada na validação](selecao-validacao.json)", ""]
    (root / "reports" / "comparacao.md").write_text("\n".join(lines), encoding="utf-8")


def run_experiment(root=None):
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    for directory in ("reports", "models"):
        (root / directory).mkdir(exist_ok=True)
    free_before = shutil.disk_usage(root).free
    frames, datasets = {}, {}
    for window, paths in WINDOWS.items():
        frames[window], datasets[window] = load_data(root, *paths)
    overlap = frames["12y"].loc[frames["12y"].ds >= frames["3y"].ds.min()].reset_index(drop=True)
    if not overlap.equals(frames["3y"]) or frames["3y"].ds.max() != END_EXCLUSIVE - pd.Timedelta(days=1):
        raise ValueError("As datas e preços comuns das duas janelas precisam ser idênticos.")
    validation, _ = evaluate_phase(root, frames, VALIDATION_START, TEST_START, "validacao")
    selected = choose_window(validation)
    selection = {"criterion": "Menor MAE na validação; empate exato favorece 3y",
                 "selected_window": selected, "selected_at_utc": datetime.now(timezone.utc).isoformat(),
                 "validation_mae_usd": {window: validation["models"][window]["mae_usd"] for window in WINDOWS}}
    save_json(root / "reports" / "selecao-validacao.json", selection)
    print(f"Escolha fixada pela validação: {selected}. Agora começa o teste reservado.", flush=True)
    test, predictions = evaluate_phase(root, frames, TEST_START, END_EXCLUSIVE, "teste")
    print(f"Ajuste final da janela escolhida ({selected}) com dados até 04/10/2026.", flush=True)
    deployment_model, seconds = fit_model(frames[selected])
    future_dates = pd.DataFrame({"ds": pd.date_range(END_EXCLUSIVE, periods=7, freq="D")})
    future_predictions = deployment_model.predict(future_dates).yhat.to_numpy()
    artifact = export_model(deployment_model, root / "models" / "modelo.json", future_dates, future_predictions)
    result = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": {"parameters": PARAMETERS, "fit_seed": SEED,
                     "selection_metric": "validation MAE", "forecast_mode": "90 days from a fixed cutoff"},
        "datasets": datasets, "validation": validation, "selection": selection, "test": test,
        "deployment": {"selected_window": selected, "train_rows": len(frames[selected]),
                       "train_start": datasets[selected]["first_date"], "train_end": "2026-10-04",
                       "fit_seconds": seconds, "independently_evaluated": False, "artifact": artifact},
        "environment": {"python": platform.python_version(), "platform": platform.system(),
                        "versions": {name: importlib.metadata.version(name) for name in
                                     ["prophet", "cmdstanpy", "holidays", "stanio", "numpy", "pandas", "matplotlib"]},
                        "disk_free_bytes_before_training": free_before,
                        "disk_free_bytes_after_training": shutil.disk_usage(root).free},
    }
    plot_test(root, predictions)
    save_json(root / "reports" / "comparacao.json", result)
    write_report(root, result)
    for window in WINDOWS:
        print(f"Teste {window}: MAE={test['models'][window]['mae_usd']:.2f} USD; "
              f"RMSE={test['models'][window]['rmse_usd']:.2f}; "
              f"sMAPE={test['models'][window]['smape_percent']:.2f}%", flush=True)
    print(f"Referência simples: MAE={test['baseline']['mae_usd']:.2f} USD", flush=True)
    return result


if __name__ == "__main__":
    run_experiment()
