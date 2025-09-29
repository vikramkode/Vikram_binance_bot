from __future__ import annotations
from typing import Optional
from src.utils import Logger, BinanceClient
from src.orders import limit_order


def run_grid(
    client: BinanceClient,
    logger: Logger,
    *,
    symbol: str,
    side: str,
    levels: int,
    lower: float,
    upper: float,
    qty: float,
    tif: str = "GTC",
    reduce_only: bool = False,
    position_side: Optional[str] = None,
) -> None:
    if levels < 2:
        raise ValueError("levels must be >= 2")
    step = (upper - lower) / (levels - 1)
    for i in range(levels):
        price = lower + i * step
        logger.info(action="grid_order", idx=i + 1, levels=levels, price=price)
        limit_order(client, logger, symbol=symbol, side=side, quantity=qty, price=price, tif=tif, reduce_only=reduce_only, position_side=position_side)
