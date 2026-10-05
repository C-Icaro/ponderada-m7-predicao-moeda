"""Contrato HTTP com artefato real, terminal e falhas de inicialização."""

import hashlib
import json
import math
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app import load_service, make_handler


class BackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.model_path = cls.root / "models/modelo.json"
        cls.original_hash = hashlib.sha256(cls.model_path.read_bytes()).hexdigest()
        cls.service = load_service(cls.model_path)
        cls.server = HTTPServer(("127.0.0.1", 0), make_handler(cls.service))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        cls.server.server_close()

    def request(self, path, payload=None, raw_body=None, content_type="application/json"):
        data = raw_body if raw_body is not None else (
            json.dumps(payload).encode("utf-8") if payload is not None else None
        )
        request = Request(self.url + path, data=data, headers={"Content-Type": content_type})
        try:
            with urlopen(request, timeout=10) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            return error.code, json.load(error)

    def test_health_after_loading_real_artifact(self):
        status, health = self.request("/health")
        self.assertEqual(status, 200)
        self.assertTrue(health["model_loaded"])
        self.assertEqual(health["trained_until"], "2026-10-04")
        self.assertEqual(health["forecast_start"], "2026-10-05")
        self.assertEqual(health["forecast_end"], "2026-10-11")
        self.assertEqual(health["model_sha256"], self.original_hash)

    def test_prediction_at_both_horizon_boundaries(self):
        for day in ["2026-10-05", "2026-10-11"]:
            with self.subTest(day=day):
                status, prediction = self.request("/predict", {"ds": day})
                self.assertEqual(status, 200)
                self.assertEqual(prediction["ds"], day)
                self.assertTrue(math.isfinite(prediction["yhat"]))
                self.assertEqual(prediction["currency"], "USD")
                self.assertEqual(prediction["model_sha256"], self.original_hash)
        self.assertEqual(hashlib.sha256(self.model_path.read_bytes()).hexdigest(), self.original_hash)

    def test_invalid_dates_and_payloads(self):
        for payload in [
            {"ds": "2026-02-30"}, {"ds": "05/10/2026"}, {"ds": "20261005"},
            {"ds": "2026-10-05T00:00:00"}, {"ds": None}, {}, ["2026-10-05"],
            {"ds": "2026-10-05", "y": 999999},
        ]:
            with self.subTest(payload=payload):
                status, response = self.request("/predict", payload)
                self.assertEqual(status, 422)
                self.assertEqual(response["error"]["code"], "invalid_input")

    def test_history_and_beyond_horizon_are_rejected(self):
        for day in ["2026-10-04", "2026-10-12"]:
            status, response = self.request("/predict", {"ds": day})
            self.assertEqual(status, 422)
            self.assertEqual(response["error"]["code"], "invalid_input")

    def test_malformed_json_and_content_type(self):
        status, _ = self.request("/predict", raw_body=b'{"ds":')
        self.assertEqual(status, 400)
        status, _ = self.request("/predict", raw_body=b"{}", content_type="text/plain")
        self.assertEqual(status, 415)
        status, _ = self.request("/predict", raw_body=b"x" * 4097)
        self.assertEqual(status, 413)

    def test_unknown_endpoint_and_wrong_method(self):
        self.assertEqual(self.request("/unknown")[0], 404)
        self.assertEqual(self.request("/predict")[0], 405)
        self.assertEqual(self.request("/health", {"ds": "2026-10-05"})[0], 405)

    def test_missing_and_corrupt_artifacts_fail_loading(self):
        with TemporaryDirectory(prefix="ponderada-backend-") as temporary:
            folder = Path(temporary)
            with self.assertRaises(ValueError):
                load_service(folder / "missing.json")
            for content in ["not-json", '{}', '{"foo": "bar"}']:
                (folder / "corrupt.json").write_text(content, encoding="utf-8")
                with self.subTest(content=content), self.assertRaises(ValueError):
                    load_service(folder / "corrupt.json")

    def test_terminal_client_calls_real_http_service(self):
        completed = subprocess.run(
            [sys.executable, str(self.root / "client/terminal.py"), "--url", self.url],
            capture_output=True, text=True, timeout=15, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn('"http_status": 200', completed.stdout)
        self.assertIn('"ds": "2026-10-05"', completed.stdout)
        self.assertIn('"yhat":', completed.stdout)

    def test_terminal_reports_non_json_http_error_without_traceback(self):
        class TextErrorHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                body = b"<html>Servico indisponivel</html>"
                self.send_response(503)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        with HTTPServer(("127.0.0.1", 0), TextErrorHandler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                completed = subprocess.run(
                    [sys.executable, str(self.root / "client/terminal.py"), "--url",
                     f"http://127.0.0.1:{server.server_port}"],
                    capture_output=True, text=True, timeout=15, check=False,
                )
                self.assertEqual(completed.returncode, 1)
                self.assertIn('"http_status": 503', completed.stdout)
                self.assertIn("Servico indisponivel", completed.stdout)
                self.assertNotIn("Traceback", completed.stderr)
            finally:
                server.shutdown()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
