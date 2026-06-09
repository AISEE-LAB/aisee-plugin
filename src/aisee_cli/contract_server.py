"""Read-only HTTP wrapper for contract context access."""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from aisee_cli.contract import build_contract_get, build_contract_manifest, build_contract_summary, validate_change_name
from aisee_cli.lookup import get_anchor, trace_anchor
from aisee_cli.output import error_response

LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


class ContractHttpError(ValueError):
    def __init__(self, status: HTTPStatus, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code


def create_contract_http_server(project_root: Path, host: str = "127.0.0.1", port: int = 0) -> ThreadingHTTPServer:
    root = project_root.resolve()

    class ContractHandler(BaseHTTPRequestHandler):
        server_version = "AiseeContractServer/1.0"

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
            try:
                status, payload = route_contract_request(root, self.path, host, self.server.server_port)
            except ContractHttpError as error:
                status = error.status
                payload = error_response(str(error), error.code)
            except ValueError as error:
                status = HTTPStatus.NOT_FOUND
                payload = error_response(str(error), "CONTRACT_HTTP_NOT_FOUND")
            except Exception as error:  # pragma: no cover - defensive HTTP boundary
                status = HTTPStatus.INTERNAL_SERVER_ERROR
                payload = error_response(str(error), "CONTRACT_HTTP_ERROR")
            self.write_json(status, payload)

        def log_message(self, _: str, *args: Any) -> None:
            return

        def write_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(int(status))
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return ThreadingHTTPServer((host, port), ContractHandler)


def serve_contract_context(project_root: Path, host: str = "127.0.0.1", port: int = 8765) -> None:
    server = create_contract_http_server(project_root, host, port)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def route_contract_request(root: Path, path: str, host: str, port: int) -> tuple[HTTPStatus, dict[str, Any]]:
    parsed = urlparse(path)
    parts = [unquote(part) for part in parsed.path.strip("/").split("/") if part]
    query = parse_qs(parsed.query)
    max_chars = parse_max_chars(query)

    if not parts or parts == ["health"]:
        return HTTPStatus.OK, {
            "status": "ok",
            "service": "aisee-contract",
            "host": host,
            "port": port,
            "warning": lan_warning(host),
        }
    if parts == ["manifest"]:
        return HTTPStatus.OK, build_contract_manifest(root, max_chars=max_chars)
    if parts == ["changes"]:
        manifest = build_contract_manifest(root, max_chars=max_chars)
        return HTTPStatus.OK, {"schema_version": "1.0", "status": "ok", "changes": manifest["changes"]}
    if len(parts) == 2 and parts[0] == "anchors":
        return HTTPStatus.OK, get_anchor(root, parts[1])
    if len(parts) == 2 and parts[0] == "trace":
        return HTTPStatus.OK, trace_anchor(root, parts[1])

    if len(parts) >= 3 and parts[0] == "changes":
        change = parts[1]
        try:
            validate_change_name(change)
        except ValueError as error:
            raise ContractHttpError(HTTPStatus.BAD_REQUEST, "CONTRACT_HTTP_BAD_REQUEST", str(error)) from error
        if parts[2] == "summary" and len(parts) == 3:
            return HTTPStatus.OK, build_contract_summary(root, change, max_chars=max_chars)
        if parts[2] == "contracts":
            if len(parts) == 3:
                summary = build_contract_summary(root, change, max_chars=max_chars)
                return HTTPStatus.OK, {
                    "schema_version": "1.0",
                    "status": "ok",
                    "change": summary["change"],
                    "contracts": summary["contracts"],
                }
            artifact = parts[3]
            if len(parts) == 4:
                return HTTPStatus.OK, build_contract_get(root, change, artifact, max_chars=max_chars)
            if len(parts) == 5 and parts[4] == "sections":
                detail = build_contract_get(root, change, artifact, max_chars=max_chars)
                return HTTPStatus.OK, {
                    "schema_version": "1.0",
                    "status": "ok",
                    "change": detail["change"],
                    "artifact": detail["artifact"],
                    "sections": detail["sections"],
                    "etag": detail["etag"],
                }
            if len(parts) == 6 and parts[4] == "sections":
                return HTTPStatus.OK, build_contract_get(
                    root,
                    change,
                    artifact,
                    section=parts[5],
                    max_chars=max_chars,
                )
        if len(parts) == 5 and parts[2] == "artifacts" and parts[4] == "raw":
            return HTTPStatus.OK, build_contract_get(
                root,
                change,
                parts[3],
                max_chars=max_chars,
                raw=True,
            )

    raise ValueError(f"unsupported contract endpoint: {parsed.path}")


def lan_warning(host: str) -> str | None:
    if host not in LOCAL_HOSTS:
        return "LAN exposure is enabled; local OpenSpec/Aisee contract artifacts may be visible to other machines."
    return None


def parse_max_chars(query: dict[str, list[str]]) -> int:
    raw = query.get("max_chars", ["4000"])[0]
    try:
        value = int(raw)
    except ValueError as error:
        raise ContractHttpError(HTTPStatus.BAD_REQUEST, "CONTRACT_HTTP_BAD_REQUEST", f"max_chars must be an integer: {raw}") from error
    if value < 1:
        raise ContractHttpError(HTTPStatus.BAD_REQUEST, "CONTRACT_HTTP_BAD_REQUEST", "max_chars must be greater than 0")
    return value
