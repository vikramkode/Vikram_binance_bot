#!/usr/bin/env python3
import os
import json
from datetime import datetime, UTC
from fpdf import FPDF

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_PATH = os.path.join(ROOT, "bot.log")
OUT_PATH = os.path.join(ROOT, "report.pdf")
REPO_URL = "https://github.com/vikramkode/Vikram_binance_bot"


def _truncate(s: str, max_len: int = 200) -> str:
    return s if len(s) <= max_len else s[: max_len - 3] + "..."


def read_recent_logs(max_lines: int = 30):
    lines = []
    if not os.path.exists(LOG_PATH):
        return lines
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for line in f.readlines()[-max_lines:]:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    # keep only a few fields to keep it tidy and remove sensitive/long bits
                    keep = {k: obj.get(k) for k in ("ts", "level", "action", "method", "path", "status", "latencyMs", "params", "reqId") if k in obj}
                    if isinstance(keep.get("params"), dict):
                        p = dict(keep["params"])  # copy
                        # drop long/sensitive values
                        p.pop("signature", None)
                        keep["params"] = p
                    lines.append(_truncate(json.dumps(keep)))
                except Exception:
                    # non-JSON or corrupted line, include as-is
                    lines.append(_truncate(line))
    except Exception as e:
        lines.append(f"<error reading log: {e}>")
    return lines


def build_report():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    epw = pdf.w - 2 * pdf.l_margin  # effective page width

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(epw, 10, "Crypto Trading Bot Assignment Report", ln=True)

    # Meta
    pdf.set_font("Helvetica", size=11)
    pdf.cell(epw, 8, f"Generated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%SZ')} (UTC)", ln=True)
    pdf.cell(epw, 8, f"Repository: {REPO_URL}", ln=True, link=REPO_URL)
    pdf.ln(4)

    # Summary section
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(epw, 8, "Summary", ln=True)
    pdf.set_font("Helvetica", size=11)
    summary = (
        "- Core: Market and Limit orders\n"
        "- Advanced: Stop-Limit, OCO, TWAP, Grid\n"
        "- Testnet/Mainnet toggle, Dry-run mode\n"
        "- Input validation (tick/step/min qty)\n"
        "- Structured JSON logs with reqId + latency"
    )
    for line in summary.split("\n"):
        pdf.multi_cell(epw, 6, line)
    pdf.ln(2)

    # How to run
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(epw, 8, "How to Run", ln=True)
    pdf.set_font("Helvetica", size=11)
    run_lines = [
        "1) python -m venv .venv",
        "2) source .venv/Scripts/activate",
        "3) pip install -r requirements.txt",
        "4) python -m src.ui_cli  # Interactive UI (Testnet + Dry-run by default)",
    ]
    for line in run_lines:
        pdf.multi_cell(epw, 6, line)
    pdf.ln(2)

    # Recent logs
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(epw, 8, "Recent bot.log entries", ln=True)
    pdf.set_font("Helvetica", size=9)
    logs = read_recent_logs(24)
    if not logs:
        pdf.multi_cell(epw, 5, "No log entries found.")
    else:
        for ln in logs:
            pdf.multi_cell(epw, 5, ln)

    pdf.output(OUT_PATH)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    build_report()
