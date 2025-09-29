from __future__ import annotations
from typing import Any, Dict, Optional
from .utils import BinanceClient, Logger, get_symbol_filters, validate_order


def market_order(client: BinanceClient, logger: Logger, *, symbol: str, side: str, quantity: float, reduce_only: bool = False, position_side: Optional[str] = None) -> Dict[str, Any]:
    info = client.exchange_info(symbol)
    filters = get_symbol_filters(info)
    validate_order(filters, qty=quantity, price=None)

    params: Dict[str, Any] = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": "MARKET",
        "quantity": quantity,
        "reduceOnly": reduce_only,
    }
    if position_side:
        params["positionSide"] = position_side

    logger.info(action="place_order", kind="market", params=params)
    return client.place_order(**params)


def limit_order(client: BinanceClient, logger: Logger, *, symbol: str, side: str, quantity: float, price: float, tif: str = "GTC", reduce_only: bool = False, position_side: Optional[str] = None) -> Dict[str, Any]:
    info = client.exchange_info(symbol)
    filters = get_symbol_filters(info)
    validate_order(filters, qty=quantity, price=price)

    params: Dict[str, Any] = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": "LIMIT",
        "timeInForce": tif,
        "quantity": quantity,
        "price": price,
        "reduceOnly": reduce_only,
    }
    if position_side:
        params["positionSide"] = position_side

    logger.info(action="place_order", kind="limit", params=params)
    return client.place_order(**params)
