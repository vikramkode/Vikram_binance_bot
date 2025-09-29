from __future__ import annotations
import os
import time
import hmac
import hashlib
from typing import Any, Dict, Optional
from uuid import uuid4
import backoff
import httpx
from dotenv import load_dotenv
import orjson
from urllib.parse import urlencode

BINANCE_FAPI_TESTNET = "https://testnet.binancefuture.com"
BINANCE_FAPI_MAINNET = "https://fapi.binance.com"

load_dotenv(override=False)


def json_dumps(data: Any) -> str:
    return orjson.dumps(data, option=orjson.OPT_NON_STR_KEYS).decode()


def get_base_url(mainnet: bool) -> str:
    return BINANCE_FAPI_MAINNET if mainnet else BINANCE_FAPI_TESTNET


def get_env_flag(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() in {"1", "true", "yes", "y"}


class Logger:
    def __init__(self, path: str = "bot.log") -> None:
        self.path = path
        # ensure file exists
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                f.write("")

    def _write(self, obj: Dict[str, Any]) -> None:
        obj.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()))
        obj.setdefault("reqId", str(uuid4()))
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json_dumps(obj) + "\n")

    def info(self, **k: Any) -> None:
        k["level"] = "INFO"
        self._write(k)

    def error(self, **k: Any) -> None:
        k["level"] = "ERROR"
        self._write(k)


class BinanceClient:
    def __init__(self, api_key: Optional[str], api_secret: Optional[str], mainnet: bool, logger: Logger, dry_run: bool = False):
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = (api_secret or os.getenv("BINANCE_API_SECRET") or "").encode()
        self.base_url = get_base_url(mainnet or get_env_flag("BINANCE_MAINNET", False))
        self.logger = logger
        self.dry_run = dry_run
        self.client = httpx.Client(base_url=self.base_url, timeout=30.0)
        self._exchange_info_cache: Dict[str, Any] = {}
        # Per-request logging correlation id set by caller (orders/strategies)
        self.current_req_id: Optional[str] = None

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Build canonical query string for Binance HMAC signing
        # Preserve insertion order of params (dicts are ordered in Py3.7+)
        query = urlencode(params, doseq=True)
        signature = hmac.new(self.api_secret, query.encode(), hashlib.sha256).hexdigest()
        return {**params, "signature": signature}

    def _headers(self) -> Dict[str, str]:
        return {"X-MBX-APIKEY": self.api_key or ""}

    @backoff.on_exception(backoff.expo, (httpx.TimeoutException, httpx.HTTPStatusError), max_tries=3)
    def _request(self, method: str, path: str, signed: bool = False, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}
        if signed:
            params.setdefault("timestamp", int(time.time() * 1000))
            params.setdefault("recvWindow", 5000)
            params = self._sign(params)
            if self.dry_run:
                # Do not hit private endpoints; return a stub response
                stub = {"dryRun": True, "method": method, "path": path, "params": params}
                # mimic order creation response
                if path == "/fapi/v1/order" and method == "POST":
                    stub.update({"orderId": int(time.time() * 1000) % 10_000_000, "status": "NEW"})
                self.logger.info(action="http-dryrun", method=method, path=path, params=params, reqId=self.current_req_id)
                return stub
        try:
            _t0 = time.perf_counter()
            resp = self.client.request(method, path, params=params, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
            latency_ms = int((time.perf_counter() - _t0) * 1000)
            self.logger.info(action="http", method=method, path=path, params=params, status=resp.status_code, latencyMs=latency_ms, reqId=self.current_req_id)
            return data
        except httpx.HTTPStatusError as e:
            latency_ms = None
            self.logger.error(action="http", method=method, path=path, params=params, status=e.response.status_code, body=e.response.text, latencyMs=latency_ms, reqId=self.current_req_id)
            raise

    # Public
    def ping(self) -> Any:
        return self._request("GET", "/fapi/v1/ping")

    def exchange_info(self, symbol: str) -> Dict[str, Any]:
        s = symbol.upper()
        if s in self._exchange_info_cache:
            return self._exchange_info_cache[s]
        data = self._request("GET", "/fapi/v1/exchangeInfo", params={"symbol": s})
        self._exchange_info_cache[s] = data
        return data

    # Private
    def place_order(self, **params: Any) -> Any:
        return self._request("POST", "/fapi/v1/order", signed=True, params=params)

    def set_leverage(self, symbol: str, leverage: int) -> Any:
        return self._request("POST", "/fapi/v1/leverage", signed=True, params={"symbol": symbol.upper(), "leverage": leverage})

    def get_order(self, symbol: str, order_id: Optional[int] = None, client_order_id: Optional[str] = None) -> Any:
        params: Dict[str, Any] = {"symbol": symbol.upper()}
        if order_id is not None:
            params["orderId"] = order_id
        if client_order_id is not None:
            params["origClientOrderId"] = client_order_id
        return self._request("GET", "/fapi/v1/order", signed=True, params=params)

    def cancel_order(self, symbol: str, order_id: Optional[int] = None, client_order_id: Optional[str] = None) -> Any:
        params: Dict[str, Any] = {"symbol": symbol.upper()}
        if order_id is not None:
            params["orderId"] = order_id
        if client_order_id is not None:
            params["origClientOrderId"] = client_order_id
        return self._request("DELETE", "/fapi/v1/order", signed=True, params=params)


def get_symbol_filters(info: Dict[str, Any]) -> Dict[str, Any]:
    sym = info["symbols"][0]
    filters = {f["filterType"]: f for f in sym["filters"]}
    return {
        "symbol": sym["symbol"],
        "pricePrecision": sym.get("pricePrecision"),
        "quantityPrecision": sym.get("quantityPrecision"),
        "tickSize": float(filters["PRICE_FILTER"]["tickSize"]),
        "stepSize": float(filters["LOT_SIZE"]["stepSize"]),
        "minQty": float(filters["LOT_SIZE"]["minQty"]),
        "minNotional": float(filters.get("MIN_NOTIONAL", {}).get("notional", 0.0)),
    }


def round_to_step(value: float, step: float) -> float:
    if step <= 0:
        return value
    return (int(value / step)) * step


def validate_order(symbol_filters: Dict[str, Any], qty: float, price: Optional[float]) -> None:
    if qty < symbol_filters["minQty"]:
        raise ValueError(f"qty {qty} < minQty {symbol_filters['minQty']}")
    if price is not None:
        px = round_to_step(price, symbol_filters["tickSize"])
        if abs(px - price) > 1e-12:
            raise ValueError(f"price {price} not aligned to tickSize {symbol_filters['tickSize']}")
    qy = round_to_step(qty, symbol_filters["stepSize"])
    if abs(qy - qty) > 1e-12:
        raise ValueError(f"qty {qty} not aligned to stepSize {symbol_filters['stepSize']}")
