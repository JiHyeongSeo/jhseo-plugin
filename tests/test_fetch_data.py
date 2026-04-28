import subprocess
import json
import sys

def run_fetch(ticker):
    result = subprocess.run(
        [sys.executable, "plugins/trading-analyst/tools/fetch_data.py", ticker],
        capture_output=True,
        text=True,
        cwd="/home/seoji/jhseo-plugin"
    )
    return result

def test_output_is_valid_json():
    result = run_fetch("AAPL")
    assert result.returncode == 0, f"stderr: {result.stderr}"
    data = json.loads(result.stdout)
    assert isinstance(data, dict)

def test_required_fields_present():
    result = run_fetch("AAPL")
    data = json.loads(result.stdout)
    assert "ticker" in data
    assert "date" in data
    assert "price" in data
    assert "technicals" in data
    assert "fundamentals" in data
    assert "news_headlines" in data

def test_price_fields():
    result = run_fetch("AAPL")
    data = json.loads(result.stdout)
    price = data["price"]
    assert "current" in price
    assert "change_1d" in price
    assert "change_1w" in price
    assert "change_1m" in price

def test_technicals_fields():
    result = run_fetch("AAPL")
    data = json.loads(result.stdout)
    t = data["technicals"]
    assert "rsi" in t
    assert "ma50" in t
    assert "ma200" in t
    assert "volume_ratio" in t

def test_fundamentals_fields():
    result = run_fetch("AAPL")
    data = json.loads(result.stdout)
    f = data["fundamentals"]
    assert "pe" in f
    assert "market_cap" in f

def test_invalid_ticker_exits_nonzero():
    result = run_fetch("INVALIDTICKER_XYZ_999")
    assert result.returncode != 0 or "error" in result.stdout.lower()

def test_ticker_in_output_matches_input():
    result = run_fetch("MSFT")
    assert result.returncode == 0, f"stderr: {result.stderr}"
    data = json.loads(result.stdout)
    assert data["ticker"] == "MSFT"
