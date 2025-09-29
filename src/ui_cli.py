from __future__ import annotations
import sys
from typing import Optional

from .utils import Logger, BinanceClient
from .orders import market_order, limit_order
from advanced.stop_limit import place_stop_limit
from advanced.oco import place_oco
from advanced.twap import run_twap
from advanced.grid import run_grid


def ask(prompt: str, default: Optional[str] = None) -> str:
    s = input(f"{prompt}{' [' + default + ']' if default else ''}: ").strip()
    return s or (default or "")


def ask_float(prompt: str, default: Optional[float] = None) -> float:
    while True:
        s = ask(prompt, str(default) if default is not None else None)
        try:
            return float(s)
        except ValueError:
            print("Please enter a number.")


def ask_int(prompt: str, default: Optional[int] = None) -> int:
    while True:
        s = ask(prompt, str(default) if default is not None else None)
        try:
            return int(s)
        except ValueError:
            print("Please enter an integer.")


def build_client(use_mainnet: bool, dry_run: bool) -> BinanceClient:
    logger = Logger()
    return BinanceClient(api_key=None, api_secret=None, mainnet=use_mainnet, logger=logger, dry_run=dry_run)


def main() -> None:
    print("Binance Futures Bot - Interactive UI (Testnet by default)")
    while True:
        print("\nChoose an action:")
        print(" 1) Market order")
        print(" 2) Limit order")
        print(" 3) Stop-Limit")
        print(" 4) OCO (TP + SL)")
        print(" 5) TWAP")
        print(" 6) Grid")
        print(" 0) Quit")
        choice = ask("Select [0-6]", "1")
        if choice == "0":
            print("Goodbye!")
            return

        symbol = ask("Symbol", "BTCUSDT").upper()
        side = ask("Side (BUY/SELL)", "BUY").upper()
        qty = ask_float("Quantity", 0.001)
        tif = ask("Time in Force (GTC/IOC/FOK)", "GTC").upper()
        leverage = ask("Leverage (empty to skip)", "").strip()
        leverage_i = int(leverage) if leverage else None
        use_mainnet = ask("Use MAINNET? (y/N)", "N").lower().startswith("y")
        dry_run = ask("Dry-run (no private calls)? (Y/n)", "Y").lower() != "n"

        client = build_client(use_mainnet, dry_run)
        if leverage_i:
            client.set_leverage(symbol, leverage_i)
        logger = client.logger

        try:
            if choice == "1":
                res = market_order(client, logger, symbol=symbol, side=side, quantity=qty)
                print({k: res.get(k) for k in ("orderId", "symbol", "status", "type", "side", "price", "origQty") if isinstance(res, dict) and k in res})
            elif choice == "2":
                price = ask_float("Limit price")
                res = limit_order(client, logger, symbol=symbol, side=side, quantity=qty, price=price, tif=tif)
                print({k: res.get(k) for k in ("orderId", "symbol", "status", "type", "side", "price", "origQty") if isinstance(res, dict) and k in res})
            elif choice == "3":
                stop = ask_float("Stop trigger price")
                limit_px = ask_float("Stop-Limit price")
                res = place_stop_limit(client, logger, symbol=symbol, side=side, quantity=qty, stop_price=stop, limit_price=limit_px, tif=tif)
                print(res)
            elif choice == "4":
                tp = ask_float("Take-profit limit price")
                stop = ask_float("Stop trigger price")
                stop_limit = ask_float("Stop-Limit price")
                res = place_oco(client, logger, symbol=symbol, side=side, quantity=qty, take_profit=tp, stop=stop, stop_limit=stop_limit, tif=tif)
                print(res)
            elif choice == "5":
                slices = ask_int("Number of slices", 5)
                interval = ask_float("Interval seconds", 30)
                otype = ask("Order type (MARKET/LIMIT)", "MARKET").upper()
                price = None
                if otype == "LIMIT":
                    price = ask_float("Limit price")
                run_twap(client, logger, symbol=symbol, side=side, qty=qty, slices=slices, interval=interval, order_type=otype, price=price, tif=tif)
                print("TWAP orders submitted.")
            elif choice == "6":
                levels = ask_int("Grid levels", 5)
                lower = ask_float("Lower price")
                upper = ask_float("Upper price")
                run_grid(client, logger, symbol=symbol, side=side, levels=levels, lower=lower, upper=upper, qty=qty, tif=tif)
                print("Grid orders submitted.")
            else:
                print("Unknown choice.")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
