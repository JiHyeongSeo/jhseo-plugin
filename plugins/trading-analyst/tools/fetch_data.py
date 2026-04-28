#!/usr/bin/env python3
"""yfinance 기반 주식 데이터 수집기. 추후 유료 API로 교체 가능한 provider 구조."""

import sys
import json
import math
import datetime
import yfinance as yf
import pandas as pd


def _safe_float(val, default=None):
    try:
        v = float(val)
        if pd.isna(v) or not math.isfinite(v):
            return default
        return round(v, 2)
    except (TypeError, ValueError):
        return default


def _calc_rsi(closes, period=14):
    delta = closes.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    last_loss = loss.iloc[-1]
    if last_loss == 0:
        return 100.0 if gain.iloc[-1] > 0 else 50.0
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return _safe_float(rsi.iloc[-1], 50)


def _calc_macd_signal(closes):
    ema12 = closes.ewm(span=12, adjust=False).mean()
    ema26 = closes.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    if macd.iloc[-1] > signal.iloc[-1]:
        return "bullish"
    elif macd.iloc[-1] < signal.iloc[-1]:
        return "bearish"
    return "neutral"


def fetch(ticker: str) -> dict:
    tk = yf.Ticker(ticker)
    hist = tk.history(period="1y")

    if hist.empty:
        print(json.dumps({"error": f"No data for ticker: {ticker}"}), file=sys.stderr)
        sys.exit(1)

    closes = hist["Close"]
    volumes = hist["Volume"]
    current = _safe_float(closes.iloc[-1])

    def pct(n):
        if len(closes) <= n:
            return None
        return round((closes.iloc[-1] / closes.iloc[-1 - n] - 1) * 100, 2)

    ma50 = _safe_float(closes.rolling(50).mean().iloc[-1])
    ma200 = _safe_float(closes.rolling(200).mean().iloc[-1])
    avg_vol = volumes.rolling(20).mean().iloc[-1]
    vol_ratio = _safe_float(volumes.iloc[-1] / avg_vol) if (avg_vol and not pd.isna(avg_vol)) else None

    info = tk.info
    market_cap_raw = info.get("marketCap")
    if market_cap_raw and market_cap_raw >= 1e12:
        market_cap = f"{market_cap_raw / 1e12:.1f}T"
    elif market_cap_raw and market_cap_raw >= 1e9:
        market_cap = f"{market_cap_raw / 1e9:.1f}B"
    else:
        market_cap = str(market_cap_raw) if market_cap_raw else "N/A"

    rev_growth = info.get("revenueGrowth")
    rev_growth_str = f"{round(rev_growth * 100, 1)}%" if rev_growth is not None else "N/A"

    news = tk.news or []
    headlines = [
        n.get("content", {}).get("title", "") or n.get("title", "")
        for n in news[:8]
        if n.get("content", {}).get("title") or n.get("title")
    ]

    return {
        "ticker": ticker.upper(),
        "date": datetime.date.today().isoformat(),
        "price": {
            "current": current,
            "change_1d": pct(1),
            "change_1w": pct(5),
            "change_1m": pct(21),
        },
        "technicals": {
            "rsi": _calc_rsi(closes),
            "macd": _calc_macd_signal(closes),
            "ma50": ma50,
            "ma200": ma200,
            "volume_ratio": vol_ratio,
        },
        "fundamentals": {
            "pe": _safe_float(info.get("trailingPE")),
            "forward_pe": _safe_float(info.get("forwardPE")),
            "eps": _safe_float(info.get("trailingEps")),
            "revenue_growth_yoy": rev_growth_str,
            "profit_margin": _safe_float(info.get("profitMargins")),
            "debt_equity": _safe_float(info.get("debtToEquity")),
            "market_cap": market_cap,
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
        },
        "news_headlines": headlines,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fetch_data.py <TICKER>", file=sys.stderr)
        sys.exit(1)
    data = fetch(sys.argv[1].upper())
    print(json.dumps(data, ensure_ascii=False, indent=2))
