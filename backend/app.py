"""API local de demonstração: carrega Prophet uma vez e atende o terminal."""

import argparse
import hashlib
import json
import math
import os
import re
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd
from prophet.serialize import model_from_json

HORIZON_DAYS = 7
MAX_BODY_BYTES = 4096


class ForecastService:
    def __init__(self, model, artifact_sha256):
        self.model = model
        self.artifact_sha256 = artifact_sha256
        history_dates = pd.to_datetime(model.history["ds"], errors="raise")
        if history_dates.empty or history_dates.isna().any():
            raise ValueError("O modelo precisa conter datas de treinamento válidas.")
        self.trained_until = history_dates.max().date()
        self.forecast_start = self.trained_until + timedelta(days=1)
        self.forecast_end = self.trained_until + timedelta(days=HORIZON_DAYS)

    def health(self):
        return {
            "status": "ok", "model_loaded": True, "model": "Prophet",
            "symbol": "BTC-USD", "currency": "USD",
            "model_sha256": self.artifact_sha256,
            "trained_until": self.trained_until.isoformat(),
            "forecast_start": self.forecast_start.isoformat(),
            "forecast_end": self.forecast_end.isoformat(),
            "horizon_days": HORIZON_DAYS,
        }

    def predict(self, payload):
        if not isinstance(payload, dict) or set(payload) != {"ds"}:
            raise ValueError('Envie somente um objeto JSON com o campo "ds".')
        value = payload["ds"]
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError("ds deve ser uma data no formato YYYY-MM-DD.")
        try:
            day = date.fromisoformat(value)
        except ValueError as error:
            raise ValueError("ds deve ser uma data válida no calendário.") from error
        if not self.forecast_start <= day <= self.forecast_end:
            raise ValueError(
                f"ds deve estar entre {self.forecast_start} e {self.forecast_end}, "
                f"os {HORIZON_DAYS} dias seguintes ao fim do treino."
            )
        frame = pd.DataFrame({"ds": [pd.Timestamp(day)]})
        prediction = float(self.model.predict(frame)["yhat"].iloc[0])
        if not math.isfinite(prediction):
            raise RuntimeError("O modelo produziu uma previsão não finita.")
        return {
            "ds": value, "yhat": prediction, "symbol": "BTC-USD", "currency": "USD",
            "model": "Prophet", "trained_until": self.trained_until.isoformat(),
            "model_sha256": self.artifact_sha256,
        }


def load_service(model_path):
    path = Path(model_path)
    try:
        content = path.read_bytes()
        model = model_from_json(content.decode("utf-8"))
        service = ForecastService(model, hashlib.sha256(content).hexdigest())
        # Só anunciamos prontidão após verificar uma previsão do artefato carregado.
        service.predict({"ds": service.forecast_start.isoformat()})
        return service
    except Exception as error:
        raise ValueError(f"Não foi possível carregar um modelo Prophet válido em {path}: {error}") from error


def make_handler(service):
    class Handler(BaseHTTPRequestHandler):
        server_version = "PonderadaComp/1.0"

        def respond(self, status, payload, allow=None):
            body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            if allow:
                self.send_header("Allow", allow)
            self.end_headers()
            self.wfile.write(body)

        def error(self, status, code, message, allow=None):
            self.respond(status, {"error": {"code": code, "message": message}}, allow)

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/health":
                self.respond(200, service.health())
            elif path == "/predict":
                self.error(405, "method_not_allowed", "Use POST para prever.", "POST")
            else:
                self.error(404, "not_found", "Endpoint inexistente.")

        def do_POST(self):
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self.error(400, "invalid_length", "Content-Length inválido.")
                return
            if length < 0:
                self.error(400, "invalid_length", "Content-Length inválido.")
                return
            self.connection.settimeout(5)
            if length > MAX_BODY_BYTES:
                # Consumir em blocos evita fechar o TCP com dados pendentes e
                # perder a resposta 413 em clientes Windows; não aloca o corpo.
                remaining = length
                try:
                    while remaining:
                        chunk = self.rfile.read(min(remaining, MAX_BODY_BYTES))
                        if not chunk:
                            break
                        remaining -= len(chunk)
                except TimeoutError:
                    pass
                self.error(413, "body_too_large", f"O corpo deve ter até {MAX_BODY_BYTES} bytes.")
                return
            try:
                body = self.rfile.read(length)
                if len(body) != length:
                    raise ValueError("Corpo incompleto.")
            except (ValueError, TimeoutError):
                self.error(400, "invalid_json", "Envie um corpo JSON UTF-8 válido e completo.")
                return
            path = urlsplit(self.path).path
            if path != "/predict":
                if path == "/health":
                    self.error(405, "method_not_allowed", "Use GET para consultar saúde.", "GET")
                else:
                    self.error(404, "not_found", "Endpoint inexistente.")
                return
            if self.headers.get_content_type() != "application/json":
                self.error(415, "unsupported_media_type", "Use Content-Type: application/json.")
                return
            if not body:
                self.error(400, "empty_body", "Envie um corpo JSON não vazio.")
                return
            try:
                payload = json.loads(body.decode("utf-8"))
            except (ValueError, UnicodeError):
                self.error(400, "invalid_json", "Envie um corpo JSON UTF-8 válido e completo.")
                return
            try:
                prediction = service.predict(payload)
            except ValueError as error:
                self.error(422, "invalid_input", str(error))
            except Exception:
                self.error(500, "prediction_failed", "Não foi possível gerar a previsão.")
            else:
                self.respond(200, prediction)

    return Handler


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=os.environ.get("MODEL_PATH", root / "models/modelo.json"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6767)
    args = parser.parse_args()
    service = load_service(args.model)
    with HTTPServer((args.host, args.port), make_handler(service)) as server:
        print(json.dumps({"listening": f"http://{args.host}:{args.port}", **service.health()}), flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        raise SystemExit(f"Inicialização interrompida: {error}") from error
