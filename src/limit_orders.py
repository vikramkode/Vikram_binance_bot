from __future__ import annotations
from typing import Any, Dict, Optional
from .orders import limit_order as _limit_order
from .utils import BinanceClient, Logger


def place(
    client: BinanceClient,
    logger: Logger,
    *,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    tif: str = "GTC",
    reduce_only: bool = False,
    position_side: Optional[str] = None,
) -> Dict[str, Any]:
    return _limit_order(client, logger, symbol=symbol, side=side, quantity=quantity, price=price, tif=tif, reduce_only=reduce_only, position_side=position_side)
