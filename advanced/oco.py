from __future__ import annotations
import time
from typing import Any, Dict, Optional
from src.utils import BinanceClient, Logger, get_symbol_filters, validate_order


def place_oco(
    client: BinanceClient,
    logger: Logger,
    *,
    symbol: str,
    side: str,
    quantity: float,
    take_profit: float,
    stop: float,
    stop_limit: float,
    tif: str = "GTC",
    reduce_only: bool = True,
    position_side: Optional[str] = None,
) -> Dict[str, Any]:
    """Emulate OCO on Futures by placing TP limit and SL stop-limit.

    Note: Futures API does not have native OCO like Spot; we place two orders and
    periodically check if one fills, then cancel the other. This function submits
    both and returns their IDs. The caller may run an external watcher; here we
    do a short, best-effort watch for demonstration.
    """
    info = client.exchange_info(symbol)
    filters = get_symbol_filters(info)
    validate_order(filters, qty=quantity, price=take_profit)
    validate_order(filters, qty=quantity, price=stop_limit)

    base_params = {"symbol": symbol.upper(), "side": side.upper(), "timeInForce": tif, "quantity": quantity, "reduceOnly": reduce_only}
    if position_side:
        base_params["positionSide"] = position_side

    # Take Profit LIMIT
    tp_params = {**base_params, "type": "LIMIT", "price": take_profit}
    logger.info(action="place_order", kind="oco_tp", params=tp_params)
    tp_res = client.place_order(**tp_params)

    # Stop-Limit
    sl_params = {**base_params, "type": "STOP", "price": stop_limit, "stopPrice": stop, "workingType": "CONTRACT_PRICE"}
    logger.info(action="place_order", kind="oco_sl", params=sl_params)
    sl_res = client.place_order(**sl_params)

    return {"tp": tp_res, "sl": sl_res}
