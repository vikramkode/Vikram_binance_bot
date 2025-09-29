from __future__ import annotations
from typing import Any, Dict, Optional
from .orders import market_order as _market_order
from .utils import BinanceClient, Logger


def place(
    client: BinanceClient,
    logger: Logger,
    *,
    symbol: str,
    side: str,
    quantity: float,
    reduce_only: bool = False,
    position_side: Optional[str] = None,
) -> Dict[str, Any]:
    return _market_order(client, logger, symbol=symbol, side=side, quantity=quantity, reduce_only=reduce_only, position_side=position_side)
