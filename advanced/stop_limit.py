from __future__ import annotations
from typing import Any, Dict, Optional
from src.utils import BinanceClient, Logger, get_symbol_filters, validate_order


def place_stop_limit(
    client: BinanceClient,
    logger: Logger,
    *,
    symbol: str,
    side: str,
    quantity: float,
    stop_price: float,
    limit_price: float,
    tif: str = "GTC",
    reduce_only: bool = False,
    position_side: Optional[str] = None,
) -> Dict[str, Any]:
    info = client.exchange_info(symbol)
    filters = get_symbol_filters(info)
    validate_order(filters, qty=quantity, price=limit_price)

    params: Dict[str, Any] = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": "STOP",
        "timeInForce": tif,
        "quantity": quantity,
        "price": limit_price,
        "stopPrice": stop_price,
        "workingType": "CONTRACT_PRICE",
        "priceProtect": True,
        "reduceOnly": reduce_only,
    }
    if position_side:
        params["positionSide"] = position_side

    logger.info(action="place_order", kind="stop_limit", params=params)
    return client.place_order(**params)
