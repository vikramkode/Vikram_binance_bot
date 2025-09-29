from __future__ import annotations
import time
from typing import Optional
from src.utils import Logger, BinanceClient
from src.orders import market_order, limit_order


def run_twap(
    client: BinanceClient,
    logger: Logger,
    *,
    symbol: str,
    side: str,
    qty: float,
    slices: int,
    interval: float,
    order_type: str = "MARKET",
    price: Optional[float] = None,
    tif: str = "GTC",
    reduce_only: bool = False,
    position_side: Optional[str] = None,
) -> None:
    per = qty / slices
    for i in range(slices):
        logger.info(action="twap_tick", idx=i + 1, slices=slices, perQty=per)
        if order_type.upper() == "MARKET":
            market_order(client, logger, symbol=symbol, side=side, quantity=per, reduce_only=reduce_only, position_side=position_side)
        else:
            if price is None:
                raise ValueError("price required for LIMIT twap")
            limit_order(client, logger, symbol=symbol, side=side, quantity=per, price=price, tif=tif, reduce_only=reduce_only, position_side=position_side)
        if i != slices - 1:
            time.sleep(interval)
