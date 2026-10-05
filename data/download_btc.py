"""Obtém o recorte diário de BTC-USD deste projeto, sem instalar pacotes."""

import argparse
import csv
import hashlib
import io
import json
import math
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat, default=date(2023, 10, 5))
    parser.add_argument("--end", type=date.fromisoformat, default=date(2026, 10, 5),
                        help="Data final exclusiva; não inclui o dia em andamento.")
    args = parser.parse_args()
    if not args.start < args.end <= datetime.now(timezone.utc).date():
        parser.error("Use início < fim <= data de hoje em UTC.")

    def timestamp(day):
        return int(datetime.combine(day, datetime.min.time(), timezone.utc).timestamp())

    url = "https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?" + urlencode({
        "period1": timestamp(args.start), "period2": timestamp(args.end), "interval": "1d",
    })
    request = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urlopen(request, timeout=25) as response:
        body = response.read()
    chart = json.loads(body)["chart"]
    if chart.get("error") or not chart.get("result"):
        raise ValueError(f"Yahoo não retornou o histórico: {chart.get('error')}")
    result = chart["result"][0]
    meta = result["meta"]
    expected = {"symbol": "BTC-USD", "currency": "USD",
                "exchangeTimezoneName": "UTC", "dataGranularity": "1d"}
    if any(meta.get(key) != value for key, value in expected.items()):
        raise ValueError("Símbolo, moeda, fuso ou frequência diferentes do contrato esperado.")

    timestamps = result["timestamp"]
    closes = result["indicators"]["quote"][0]["close"]
    if len(timestamps) != len(closes):
        raise ValueError("Quantidade de datas diferente da quantidade de fechamentos.")
    rows = []
    for stamp, close in zip(timestamps, closes):
        day = datetime.fromtimestamp(stamp, timezone.utc).date()
        # O Yahoo pode incluir uma observação adicional, apesar do limite solicitado.
        if not args.start <= day < args.end:
            continue
        if close is None or not math.isfinite(float(close)) or float(close) <= 0:
            raise ValueError(f"Fechamento ausente ou inválido em {day}.")
        rows.append((day, float(close)))
    rows.sort()
    expected_days = [args.start + timedelta(days=i)
                     for i in range((args.end - args.start).days)]
    if [day for day, _ in rows] != expected_days:
        raise ValueError("Histórico incompleto ou com datas duplicadas. Nenhum valor foi preenchido.")

    content = io.StringIO(newline="")
    writer = csv.writer(content, lineterminator="\n")
    writer.writerow(["ds", "y"])
    writer.writerows((day.isoformat(), close) for day, close in rows)
    csv_bytes = content.getvalue().encode("utf-8")
    root = Path(__file__).resolve().parent
    output = root / "processed" / "btc_usd_daily.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(csv_bytes)

    provenance = {
        "source": "Yahoo Finance", "history_page": "https://finance.yahoo.com/quote/BTC-USD/history/",
        "request_url": url, "method": "Python standard library / Yahoo chart endpoint",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(), **expected,
        "start_inclusive": args.start.isoformat(), "end_exclusive": args.end.isoformat(),
        "first_date": rows[0][0].isoformat(), "last_date": rows[-1][0].isoformat(),
        "rows": len(rows), "response_rows": len(timestamps), "response_bytes": len(body),
        "excluded_outside_period": len(timestamps) - len(rows),
        "csv_path": "data/processed/btc_usd_daily.csv", "csv_bytes": len(csv_bytes),
        "csv_sha256": hashlib.sha256(csv_bytes).hexdigest(),
        "columns": {"ds": "Data diária da fonte UTC, YYYY-MM-DD, sem timezone",
                    "y": "Close não ajustado, USD por BTC"},
        "validation": {"complete_daily_range": True, "duplicate_dates": 0,
                       "missing_dates": 0, "invalid_closes": 0},
        "redistribution": "CSV local ignorado pelo Git; repositório contém obtenção e procedência.",
    }
    (root / "coleta-btc-usd.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Salvo: {output}")
    print(f"{len(rows)} linhas | {rows[0][0]} a {rows[-1][0]} | {len(csv_bytes)} bytes")
    print(f"Excluídas fora do período: {len(timestamps) - len(rows)}")


if __name__ == "__main__":
    try:
        main()
    except (URLError, ValueError, KeyError, TypeError, IndexError) as error:
        raise SystemExit(f"Coleta interrompida: {error}") from error
