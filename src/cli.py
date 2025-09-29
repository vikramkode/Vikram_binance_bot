from __future__ import annotations
import argparse
import os
import sys
from typing import Optional
from rich import print as rprint

from .utils import Logger, BinanceClient, get_env_flag
from .orders import market_order, limit_order
from advanced.stop_limit import place_stop_limit
from advanced.oco import place_oco
from advanced.twap import run_twap
from advanced.grid import run_grid


def make_client(args) -> BinanceClient:
    logger = Logger()
    # If --testnet provided, force mainnet False; otherwise use --mainnet flag
    mainnet = False
    if getattr(args, "testnet", False):
        mainnet = False
    else:
        mainnet = bool(getattr(args, "mainnet", False))
    client = BinanceClient(api_key=os.getenv("BINANCE_API_KEY"), api_secret=os.getenv("BINANCE_API_SECRET"), mainnet=mainnet, logger=logger, dry_run=args.dry_run)
    return client


def cmd_order(args) -> None:
    logger = Logger()
    client = make_client(args)
    # correlate logs for this command
    import uuid
    client.current_req_id = str(uuid.uuid4())

    if args.leverage:
        client.set_leverage(args.symbol, args.leverage)

    if args.type.upper() == "MARKET":
        res = market_order(client, logger, symbol=args.symbol, side=args.side, quantity=args.qty, reduce_only=args.reduce_only, position_side=args.position_side)
    elif args.type.upper() == "LIMIT":
        if args.price is None:
            rprint("[red]--price is required for LIMIT orders[/red]")
            sys.exit(1)
        res = limit_order(client, logger, symbol=args.symbol, side=args.side, quantity=args.qty, price=args.price, tif=args.tif, reduce_only=args.reduce_only, position_side=args.position_side)
    else:
        rprint(f"[red]Unsupported type: {args.type}[/red]")
        sys.exit(1)

    rprint({k: res.get(k) for k in ("orderId", "symbol", "status", "price", "origQty", "type", "side") if k in res})


def cmd_stop_limit(args) -> None:
    logger = Logger()
    client = make_client(args)
    import uuid
    client.current_req_id = str(uuid.uuid4())
    if args.leverage:
        client.set_leverage(args.symbol, args.leverage)
    res = place_stop_limit(client, logger, symbol=args.symbol, side=args.side, quantity=args.qty, stop_price=args.stop, limit_price=args.price, tif=args.tif, reduce_only=args.reduce_only, position_side=args.position_side)
    rprint(res)


def cmd_oco(args) -> None:
    logger = Logger()
    client = make_client(args)
    import uuid
    client.current_req_id = str(uuid.uuid4())
    if args.leverage:
        client.set_leverage(args.symbol, args.leverage)
    res = place_oco(client, logger, symbol=args.symbol, side=args.side, quantity=args.qty, take_profit=args.take_profit, stop=args.stop, stop_limit=args.stop_limit, tif=args.tif, reduce_only=args.reduce_only, position_side=args.position_side)
    rprint(res)


def cmd_twap(args) -> None:
    logger = Logger()
    client = make_client(args)
    import uuid
    client.current_req_id = str(uuid.uuid4())
    if args.leverage:
        client.set_leverage(args.symbol, args.leverage)
    run_twap(client, logger, symbol=args.symbol, side=args.side, qty=args.qty, slices=args.slices, interval=args.interval, order_type=args.type, price=args.price, tif=args.tif, reduce_only=args.reduce_only, position_side=args.position_side)


def cmd_grid(args) -> None:
    logger = Logger()
    client = make_client(args)
    import uuid
    client.current_req_id = str(uuid.uuid4())
    if args.leverage:
        client.set_leverage(args.symbol, args.leverage)
    run_grid(client, logger, symbol=args.symbol, side=args.side, levels=args.levels, lower=args.lower, upper=args.upper, qty=args.qty, tif=args.tif, reduce_only=args.reduce_only, position_side=args.position_side)



def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Binance USDT-M Futures CLI Bot")
    sub = p.add_subparsers(required=True)

    # Shared flags function
    def add_common(o):
        o.add_argument("--symbol", required=True)
        o.add_argument("--side", required=True, choices=["BUY", "SELL"])
        o.add_argument("--qty", type=float, required=True)
        o.add_argument("--tif", default="GTC", choices=["GTC", "IOC", "FOK"])
        o.add_argument("--reduce-only", action="store_true", dest="reduce_only")
        o.add_argument("--position-side", choices=["LONG", "SHORT"], default=None)
        o.add_argument("--leverage", type=int, default=None)
        o.add_argument("--mainnet", action="store_true")
        o.add_argument("--testnet", action="store_true")
        o.add_argument("--dry-run", action="store_true", dest="dry_run")
    # order
    po = sub.add_parser("order", help="Place MARKET or LIMIT order")
    add_common(po)
    po.add_argument("--type", required=True, choices=["MARKET", "LIMIT"])
    po.add_argument("--price", type=float)
    po.set_defaults(func=cmd_order)

    # stop-limit
    ps = sub.add_parser("stop-limit", help="Place STOP_LIMIT order")
    add_common(ps)
    ps.add_argument("--stop", type=float, required=True)
    ps.add_argument("--price", type=float, required=True)
    ps.set_defaults(func=cmd_stop_limit)

    # oco
    po2 = sub.add_parser("oco", help="Place OCO bracket (TP + SL)")
    add_common(po2)
    po2.add_argument("--take-profit", type=float, required=True)
    po2.add_argument("--stop", type=float, required=True)
    po2.add_argument("--stop-limit", type=float, required=True)
    po2.set_defaults(func=cmd_oco)

    # twap
    pt = sub.add_parser("twap", help="Run TWAP strategy")
    add_common(pt)
    pt.add_argument("--slices", type=int, required=True)
    pt.add_argument("--interval", type=float, required=True, help="seconds between orders")
    pt.add_argument("--type", choices=["MARKET", "LIMIT"], default="MARKET")
    pt.add_argument("--price", type=float)
    pt.set_defaults(func=cmd_twap)

    # grid
    pg = sub.add_parser("grid", help="Run Grid strategy")
    add_common(pg)
    pg.add_argument("--levels", type=int, required=True)
    pg.add_argument("--lower", type=float, required=True)
    pg.add_argument("--upper", type=float, required=True)
    pg.set_defaults(func=cmd_grid)

    return p


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
