"""Comparação exploratória ARIMA, sem alterar a seleção ou o artefato Prophet."""

import hashlib
import importlib.metadata
import json
import platform
import warnings
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from train_compare import (END_EXCLUSIVE, TEST_START, VALIDATION_START, WINDOWS,
                           load_data, metrics, save_json, training_before)

ORDERS = ((0, 1, 0), (1, 1, 0), (0, 1, 1), (1, 1, 1))
SCALE = 1000.0
TIE_USD = 1e-6


def build_model(train, order):
    series = pd.Series(train.y.to_numpy() / SCALE,
                       index=pd.DatetimeIndex(train.ds, freq="D"), name="price")
    return ARIMA(series, order=order, trend="n", enforce_stationarity=True,
                 enforce_invertibility=True)


def predict(result, dates):
    values = result.forecast(steps=len(dates))
    if list(values.index) != list(dates):
        raise ValueError("As datas previstas não correspondem ao bloco futuro solicitado.")
    values = values.to_numpy() * SCALE
    if not np.isfinite(values).all():
        raise ValueError("ARIMA produziu previsão não finita.")
    return values


def fit_candidate(train, observed, order):
    started = perf_counter()
    item = {"order": list(order), "train_rows": len(train),
            "train_start": train.ds.iloc[0].date().isoformat(),
            "train_end": train.ds.iloc[-1].date().isoformat()}
    result = None
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        try:
            result = build_model(train, order).fit(method_kwargs={"maxiter": 200})
            item["converged"] = bool(result.mle_retvals.get("converged", False))
            if not item["converged"]:
                raise ValueError("O otimizador não convergiu no limite fixado.")
            values = predict(result, observed.ds)
            if "y" in observed:
                item.update(metrics(observed.y, values))
            item["eligible"] = True
        except (ValueError, np.linalg.LinAlgError, FloatingPointError) as error:
            item.update(eligible=False, error=str(error))
            result = None
        item["warnings"] = [f"{w.category.__name__}: {w.message}" for w in captured]
    item["fit_seconds"] = perf_counter() - started
    return item, result


def choose_candidate(candidates):
    eligible = [item for item in candidates if item["eligible"]]
    if not eligible:
        raise ValueError("Nenhum candidato ARIMA convergiu com previsão válida.")
    minimum = min(item["mae_usd"] for item in eligible)
    tied = [item for item in eligible if item["mae_usd"] <= minimum + TIE_USD]
    return min(tied, key=lambda item: (item["order"][0] + item["order"][2],
                                       item["order"][0], item["order"][2]))


def load_export(path):
    restored = json.loads(path.read_text(encoding="utf-8"))
    expected = {"format": "ponderada-arima-v1", "statsmodels_version":
                importlib.metadata.version("statsmodels"), "trend": "n", "scale_usd": SCALE,
                "enforce_stationarity": True, "enforce_invertibility": True}
    if any(restored.get(key) != value for key, value in expected.items()):
        raise ValueError("Formato, versão ou configuração do artefato ARIMA incompatível.")
    if tuple(restored["order"]) not in ORDERS:
        raise ValueError("Ordem ARIMA não pertence ao protocolo.")
    frame = pd.DataFrame({"ds": pd.date_range(restored["train_start"],
                                               restored["train_end"], freq="D"),
                          "y": restored["train_prices_usd"]})
    if not np.isfinite(frame.y).all() or (frame.y <= 0).any():
        raise ValueError("Preços inválidos no artefato ARIMA.")
    model = build_model(frame, tuple(restored["order"]))
    if model.param_names != restored["param_names"] or len(model.param_names) != len(restored["params"]):
        raise ValueError("Parâmetros ARIMA incompatíveis.")
    if not np.isfinite(restored["params"]).all():
        raise ValueError("Parâmetros ARIMA não finitos.")
    return model.filter(restored["params"])


def export_model(result, train, order, path, dates):
    artifact = {"format": "ponderada-arima-v1", "statsmodels_version":
                importlib.metadata.version("statsmodels"), "order": list(order),
                "trend": "n", "scale_usd": SCALE, "enforce_stationarity": True,
                "enforce_invertibility": True, "train_start": train.ds.iloc[0].date().isoformat(),
                "train_end": train.ds.iloc[-1].date().isoformat(),
                "train_prices_usd": train.y.tolist(), "param_names": result.param_names,
                "params": result.params.tolist()}
    save_json(path, artifact)
    loaded = load_export(path)
    original, reloaded = predict(result, dates), predict(loaded, dates)
    if not np.allclose(original, reloaded, rtol=0, atol=1e-6):
        raise RuntimeError("A reconstrução JSON alterou as previsões ARIMA.")
    return {"path": "models/" + path.name, "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "reload_max_abs_difference": float(np.max(np.abs(original - reloaded)))}


def write_report(root, report, predictions):
    lines = ["# ARIMA versus Prophet: comparação exploratória", "",
             "O teste Prophet já havia sido observado. Ordens e desempates ARIMA foram fixados "
             "antes dos ajustes; o resultado não constitui um novo teste intocado.", "",
             "## Validação: escolha da ordem", "",
             "| Histórico | Ordem | Convergiu | MAE (USD) |",
             "| --- | --- | --- | ---: |"]
    for window, candidates in report["validation_candidates"].items():
        for item in candidates:
            value = f'{item["mae_usd"]:.2f}' if item["eligible"] else "excluído"
            lines.append(f'| {window} | {tuple(item["order"])} | {item.get("converged", False)} | {value} |')
    lines += ["", f'Janela escolhida pela validação: **{report["selection"]["selected_window"]}**. '
              "As ordens escolhidas e os avisos estão no JSON completo.", "",
              "## Teste de 07/07/2026 a 04/10/2026", "",
              "| Modelo | MAE (USD) | RMSE (USD) | sMAPE (%) |",
              "| --- | ---: | ---: | ---: |"]
    for label, item in report["test_comparison"].items():
        lines.append(f'| {label} | {item["mae_usd"]:.2f} | {item["rmse_usd"]:.2f} | {item["smape_percent"]:.2f} |')
    lines += ["", "![Previsões no teste](arima-teste.png)", "",
              "Cada modelo prevê os mesmos 90 dias de uma vez, sem incorporar preços do bloco. "
              "ARIMA(0,1,0) sem drift equivale à referência do último fechamento. "
              "Um resultado melhor neste recorte não comprova generalização ou ganho financeiro.", "",
              "O ajuste final ARIMA está em `models/arima.json`, separado de `models/modelo.json` "
              "(Prophet, usado pelo backend). O ajuste final não foi avaliado em dados posteriores. "
              "JSONs foram reconstruídos e suas previsões conferidas; arquivos gerados ficam fora do Git.", "",
              "[Protocolo](../training/protocolo-arima.md), [notebook](../training/arima.ipynb), "
              "[resultados e hashes](arima.json) e [seleção registrada](selecao-arima.json).", ""]
    (root / "reports/arima.md").write_text("\n".join(lines), encoding="utf-8")
    fig, ax = plt.subplots(figsize=(11, 5))
    for column, label, style in [("y", "Observado", "-"), ("arima_3y", "ARIMA: 3 anos", "-"),
                                  ("arima_12y", "ARIMA: 12 anos", "-"),
                                  ("3y", "Prophet: 3 anos", ":"),
                                  ("12y", "Prophet: 12 anos", ":"),
                                  ("baseline", "Último fechamento", "--")]:
        ax.plot(predictions.ds, predictions[column], label=label, linestyle=style)
    ax.set(title="BTC-USD: confronto exploratório, previsão de 90 dias no corte de 06/07/2026",
           ylabel="USD por BTC", xlabel="Data")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(root / "reports/arima-teste.png", dpi=140)
    plt.close(fig)


def run_experiment(root=None):
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    frames, datasets = {}, {}
    for window, paths in WINDOWS.items():
        frames[window], datasets[window] = load_data(root, *paths)
    common = frames["12y"].loc[frames["12y"].ds >= frames["3y"].ds.min()].reset_index(drop=True)
    if not frames["3y"].equals(common):
        raise ValueError("Os preços nas datas comuns precisam coincidir.")
    prophet_path = root / "reports/comparacao.json"
    prophet = json.loads(prophet_path.read_text(encoding="utf-8"))
    if any(datasets[w]["sha256"] != prophet["datasets"][w]["sha256"] for w in WINDOWS):
        raise ValueError("Prophet foi avaliado em outra versão dos dados.")
    observed = frames["3y"].loc[(frames["3y"].ds >= VALIDATION_START) &
                               (frames["3y"].ds < TEST_START)].copy()
    candidates, winners = {}, {}
    for window in WINDOWS:
        train = training_before(frames[window], VALIDATION_START)
        candidates[window] = []
        for order in ORDERS:
            print(f"Validação ARIMA {window}, ordem {order}", flush=True)
            item, _ = fit_candidate(train, observed, order)
            candidates[window].append(item)
        winners[window] = choose_candidate(candidates[window])
    selected = "3y" if winners["3y"]["mae_usd"] <= winners["12y"]["mae_usd"] + TIE_USD else "12y"
    selection = {"selected_window": selected,
                 "orders_by_window": {w: winners[w]["order"] for w in WINDOWS},
                 "validation_mae_usd": {w: winners[w]["mae_usd"] for w in WINDOWS},
                 "selected_at_utc": datetime.now(timezone.utc).isoformat(),
                 "criterion": "MAE de validação; empates conforme protocolo-arima.md"}
    save_json(root / "reports/selecao-arima.json", selection)
    observed = frames["3y"].loc[(frames["3y"].ds >= TEST_START) &
                               (frames["3y"].ds < END_EXCLUSIVE)].reset_index(drop=True)
    predictions = pd.read_csv(root / "reports/predicoes-teste.csv", parse_dates=["ds"])
    if not predictions[["ds", "y"]].equals(observed):
        raise ValueError("Previsões Prophet não correspondem às datas e preços de teste.")
    for column in ("3y", "12y", "baseline"):
        reference = prophet["test"]["baseline"] if column == "baseline" else prophet["test"]["models"][column]
        calculated = metrics(predictions.y, predictions[column])
        if any(not np.isclose(calculated[k], reference[k], rtol=1e-10, atol=1e-6) for k in calculated):
            raise ValueError("CSV de previsões Prophet não confere com suas métricas registradas.")
    tests, comparison = {}, {}
    for window in WINDOWS:
        train = training_before(frames[window], TEST_START)
        order = tuple(winners[window]["order"])
        print(f"Teste ARIMA {window}, ordem {order}", flush=True)
        item, result = fit_candidate(train, observed, order)
        if result is None:
            raise RuntimeError(f"O ajuste de teste {window} falhou: {item}")
        predictions["arima_" + window] = predict(result, observed.ds)
        item["artifact"] = export_model(result, train, order, root / f"models/arima-{window}.json", observed.ds)
        tests[window] = item
        comparison[f"ARIMA {window} {order}"] = {k: item[k] for k in metrics(observed.y, predictions["arima_" + window])}
    for window in WINDOWS:
        comparison["Prophet " + window] = {k: prophet["test"]["models"][window][k]
                                           for k in ("mae_usd", "rmse_usd", "smape_percent")}
    comparison["Último fechamento"] = {k: prophet["test"]["baseline"][k]
                                       for k in ("mae_usd", "rmse_usd", "smape_percent")}
    predictions.to_csv(root / "reports/predicoes-arima-teste.csv", index=False)
    dates = pd.Series(pd.date_range(END_EXCLUSIVE, periods=90, freq="D"))
    train = frames[selected]
    future = pd.DataFrame({"ds": dates})
    order = tuple(winners[selected]["order"])
    final_item, result = fit_candidate(train, future, order)
    if result is None:
        raise RuntimeError(f"O ajuste final falhou: {final_item}")
    final = {k: v for k, v in final_item.items() if k not in ("mae_usd", "rmse_usd", "smape_percent")}
    final["artifact"] = export_model(result, train, order, root / "models/arima.json", dates)
    final["independently_evaluated"] = False
    report = {"created_at_utc": datetime.now(timezone.utc).isoformat(),
              "protocol": {"orders": ORDERS, "trend": "n", "scale_usd": SCALE,
                           "maxiter": 200, "tie_usd": TIE_USD, "exploratory": True,
                           "forecast_mode": "90 days from a fixed cutoff"},
              "datasets": datasets, "validation_candidates": candidates,
              "selection": selection, "test_models": tests, "test_comparison": comparison,
              "test_start": TEST_START.date().isoformat(),
              "test_end": (END_EXCLUSIVE - pd.Timedelta(days=1)).date().isoformat(),
              "final_refit": final, "prophet_report_sha256": hashlib.sha256(prophet_path.read_bytes()).hexdigest(),
              "environment": {"python": platform.python_version(), **{name: importlib.metadata.version(name)
                              for name in ("statsmodels", "scipy", "numpy", "pandas")}}}
    save_json(root / "reports/arima.json", report)
    write_report(root, report, predictions)
    return report


if __name__ == "__main__":
    run_experiment()
