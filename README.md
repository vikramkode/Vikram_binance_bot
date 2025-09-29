# Binance USDT-M Futures CLI Bot

A CLI trading bot for Binance USDT-M Futures with market and limit orders, plus optional advanced strategies (Stop-Limit, OCO, TWAP, Grid). Includes structured JSON logging and robust input validation.

## Features
- Core:
  - Market orders
  - Limit orders
- Advanced (bonus):
  - Stop-Limit orders
  - OCO (one-cancels-the-other)
  - TWAP (time-weighted average price)
  - Grid strategy (ladder buy/sell)
- Input validation against exchange filters
- Structured JSON logs in `bot.log`
- Testnet/mainnet toggle, dry-run mode, leverage configuration

## Requirements
- Python 3.10+
- Dependencies in `requirements.txt`
- Binance API key/secret (testnet strongly recommended for development)

## Setup
1. Create and activate a virtual environment.
2. Install dependencies.
3. Copy `.env.example` to `.env` and fill in your keys.

Windows (PowerShell)
```powershell
# 1) Create venv
py -3 -m venv .venv
./.venv/Scripts/Activate.ps1

# 2) Install deps
pip install -r requirements.txt

# 3) Configure environment
copy .env.example .env
# edit .env to set BINANCE_API_KEY, BINANCE_API_SECRET
```

Windows (CMD)
```bat
py -3 -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
```

Unix-like shells (Git Bash, WSL, macOS)
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
```

## Quick Start
Examples use testnet. Add `--mainnet` to hit production at your own risk. Use `--dry-run` to avoid sending signed requests (simulated responses).

- Market Buy BTCUSDT 0.001
```bash
python -m src.cli order --type MARKET --side BUY --symbol BTCUSDT --qty 0.001 --testnet
```

- Limit Sell with GTC
```bash
python -m src.cli order --type LIMIT --side SELL --symbol BTCUSDT --qty 0.001 --price 70000 --tif GTC --testnet
```

- Stop-Limit (trigger 69000, place limit 68950)
```bash
python -m src.cli stop-limit --side SELL --symbol BTCUSDT --qty 0.001 --stop 69000 --price 68950 --tif GTC --testnet
```

- OCO (TP 72000, SL 68500)
```bash
python -m src.cli oco --side SELL --symbol BTCUSDT --qty 0.001 --take-profit 72000 --stop 68500 --stop-limit 68450 --tif GTC --testnet
```

- TWAP: split 0.01 into 5 orders, every 30s
```bash
python -m src.cli twap --side BUY --symbol BTCUSDT --qty 0.01 --slices 5 --interval 30 --type LIMIT --price 69500 --tif GTC --testnet
```

- Grid: 5 levels from 68000 to 72000
```bash
python -m src.cli grid --side SELL --symbol BTCUSDT --levels 5 --lower 68000 --upper 72000 --qty 0.001 --tif GTC --testnet
```

## Logs
- All actions are written to `bot.log` in JSON Lines format. Each line contains timestamp, level, action, request/response metadata, and any errors.

## Optional simple UI (interactive CLI)
Prefer prompts over flags? Run the interactive UI:

```powershell
python -m src.ui_cli
```

It will ask for symbol, side, quantity, and which strategy to use (Market/Limit/Stop-Limit/OCO/TWAP/Grid), then submit via the same modules.

## Files
- `src/` — core app code (client, validators, CLI, market/limit modules)
- `advanced/` — advanced strategies (stop-limit, oco, twap, grid)
- `bot.log` — structured JSON log file
- `report.pdf` — add screenshots and analysis here

## Safety & Notes
- Prefer `--testnet` until you fully understand what your bot will do.
- Respect Binance rate limits; we include backoff + retries.
- Ensure quantities and prices meet symbol filters (tickSize/stepSize/minNotional).

## License
For educational purposes only. Trading carries risk. Use at your own responsibility.