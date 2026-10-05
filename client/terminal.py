"""Cliente terminal que consulta saúde e solicita uma previsão por HTTP."""

import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request_json(base_url, path, payload=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = Request(base_url.rstrip("/") + path, data=body, headers=headers)
    with urlopen(request, timeout=10) as response:
        return {"http_status": response.status, "body": json.load(response)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ds", nargs="?", help="Data YYYY-MM-DD; omita para usar forecast_start retornado por /health.")
    parser.add_argument("--url", default="http://127.0.0.1:6767")
    args = parser.parse_args()
    health = request_json(args.url, "/health")
    print(json.dumps({"health": health}, ensure_ascii=False, indent=2))
    day = args.ds or health["body"]["forecast_start"]
    prediction = request_json(args.url, "/predict", {"ds": day})
    print(json.dumps({"prediction": prediction}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except HTTPError as error:
        content = error.read().decode("utf-8", errors="replace")
        try:
            response_body = json.loads(content)
        except ValueError:
            response_body = {"message": content or error.reason}
        print(json.dumps({"http_status": error.code, "body": response_body}, ensure_ascii=False, indent=2))
        raise SystemExit(1) from error
    except (URLError, ValueError, KeyError, OSError) as error:
        raise SystemExit(f"Consulta interrompida: {error}") from error
