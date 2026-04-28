# Trading Analyst Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/analyze <TICKER>` 슬래시 커맨드로 미국 주식을 다중 에이전트가 분석해 BUY/HOLD/SELL을 터미널에 출력하는 Claude Code 플러그인 구현.

**Architecture:** yfinance로 수집한 데이터를 기술적/펀더멘털/뉴스 에이전트가 병렬 분석하고, Bull/Bear 토론 후 Research Manager → Portfolio Manager가 최종 결정을 내린다. 모든 에이전트는 Claude Code의 Agent 툴로 소환되어 구독 비용 내에서 동작한다.

**Tech Stack:** Python 3.10+, yfinance, pandas, Claude Code Agent tool, WebSearch tool

---

## 파일 구조

```
plugins/trading-analyst/
├── .claude-plugin/
│   └── plugin.json                  # 신규 생성
├── SKILL.md                         # 신규 생성
├── commands/
│   └── analyze.md                   # 신규 생성 — 오케스트레이터
└── tools/
    └── fetch_data.py                # 신규 생성 — yfinance 수집기

.claude-plugin/marketplace.json      # 기존 수정 — 플러그인 등록
tests/
└── test_fetch_data.py               # 신규 생성
```

---

## Task 1: fetch_data.py — yfinance 데이터 수집기

**Files:**
- Create: `plugins/trading-analyst/tools/fetch_data.py`
- Create: `tests/test_fetch_data.py`

- [ ] **Step 1: 테스트 파일 작성**

`tests/test_fetch_data.py` 생성:

```python
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
    # yfinance returns empty data for invalid tickers — should exit with error
    assert result.returncode != 0 or "error" in result.stdout.lower()

def test_ticker_in_output_matches_input():
    result = run_fetch("MSFT")
    data = json.loads(result.stdout)
    assert data["ticker"] == "MSFT"
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
cd /home/seoji/jhseo-plugin
python -m pytest tests/test_fetch_data.py -v 2>&1 | head -30
```

Expected: `ModuleNotFoundError` 또는 `FileNotFoundError` (fetch_data.py 없음)

- [ ] **Step 3: fetch_data.py 구현**

`plugins/trading-analyst/tools/` 디렉터리 생성 후 `fetch_data.py` 작성:

```python
#!/usr/bin/env python3
"""yfinance 기반 주식 데이터 수집기. 추후 유료 API로 교체 가능한 provider 구조."""

import sys
import json
import datetime
import yfinance as yf
import pandas as pd


def _safe_float(val, default=None):
    try:
        v = float(val)
        return None if pd.isna(v) else round(v, 2)
    except (TypeError, ValueError):
        return default


def _calc_rsi(closes, period=14):
    delta = closes.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, float("inf"))
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
    hist = tk.history(period="6mo")

    if hist.empty:
        print(json.dumps({"error": f"No data for ticker: {ticker}"}), file=sys.stderr)
        sys.exit(1)

    closes = hist["Close"]
    volumes = hist["Volume"]
    current = _safe_float(closes.iloc[-1])

    # 가격 변화율
    def pct(n):
        if len(closes) <= n:
            return None
        return round((closes.iloc[-1] / closes.iloc[-1 - n] - 1) * 100, 2)

    # 기술 지표
    ma50 = _safe_float(closes.rolling(50).mean().iloc[-1])
    ma200 = _safe_float(closes.rolling(200).mean().iloc[-1])
    avg_vol = volumes.rolling(20).mean().iloc[-1]
    vol_ratio = round(volumes.iloc[-1] / avg_vol, 2) if avg_vol else None

    # 펀더멘털
    info = tk.info
    market_cap_raw = info.get("marketCap")
    if market_cap_raw and market_cap_raw >= 1e12:
        market_cap = f"{market_cap_raw / 1e12:.1f}T"
    elif market_cap_raw and market_cap_raw >= 1e9:
        market_cap = f"{market_cap_raw / 1e9:.1f}B"
    else:
        market_cap = str(market_cap_raw) if market_cap_raw else "N/A"

    rev_growth = info.get("revenueGrowth")
    rev_growth_str = f"{round(rev_growth * 100, 1)}%" if rev_growth else "N/A"

    # 뉴스
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
```

- [ ] **Step 4: 테스트 실행 — 통과 확인**

```bash
cd /home/seoji/jhseo-plugin
python -m pytest tests/test_fetch_data.py -v
```

Expected: 7개 테스트 모두 PASS (네트워크 필요)

- [ ] **Step 5: 수동 확인**

```bash
cd /home/seoji/jhseo-plugin
python plugins/trading-analyst/tools/fetch_data.py NVDA | python -m json.tool | head -40
```

Expected: 정형화된 JSON 출력

- [ ] **Step 6: 커밋**

```bash
cd /home/seoji/jhseo-plugin
git add plugins/trading-analyst/tools/fetch_data.py tests/test_fetch_data.py
git commit -m "feat: add fetch_data.py yfinance data collector"
```

---

## Task 2: plugin.json — 플러그인 메타데이터

**Files:**
- Create: `plugins/trading-analyst/.claude-plugin/plugin.json`

- [ ] **Step 1: 파일 작성**

```json
{
  "name": "trading-analyst",
  "description": "미국 주식 다중 에이전트 분석. /analyze <TICKER>로 BUY/HOLD/SELL 결론 도출",
  "version": "1.0.0",
  "author": {
    "name": "JiHyeong Seo"
  },
  "keywords": [
    "trading",
    "stock",
    "analysis",
    "finance",
    "미국주식",
    "주식분석"
  ]
}
```

- [ ] **Step 2: 커밋**

```bash
cd /home/seoji/jhseo-plugin
git add plugins/trading-analyst/.claude-plugin/plugin.json
git commit -m "feat: add trading-analyst plugin.json"
```

---

## Task 3: SKILL.md — 플러그인 스킬 설명

**Files:**
- Create: `plugins/trading-analyst/SKILL.md`

- [ ] **Step 1: 파일 작성**

```markdown
---
name: trading-analyst
description: 미국 주식 종목 다중 에이전트 분석 플러그인. "주식 분석", "analyze", "trading", "BUY SELL", "종목 분석" 키워드에서 활성화
---

# Trading Analyst

미국 주식 종목을 다중 에이전트 파이프라인으로 분석하는 플러그인입니다.

기술적 분석, 펀더멘털 분석, 뉴스/감성 분석을 병렬로 수행하고
Bull/Bear 토론 → Research Manager → Portfolio Manager 순으로 종합해
BUY / HOLD / SELL 결론과 신뢰도를 터미널에 출력합니다.

## 사용법

```
/analyze NVDA
/analyze AAPL
/analyze TSLA
```

## 의존성

- Python 3.10+
- `yfinance` (`pip install yfinance`)
- `pandas` (`pip install pandas`)

## 소요 시간

약 3~5분 (6개 에이전트 순차+병렬 실행)
```

- [ ] **Step 2: 커밋**

```bash
cd /home/seoji/jhseo-plugin
git add plugins/trading-analyst/SKILL.md
git commit -m "feat: add trading-analyst SKILL.md"
```

---

## Task 4: analyze.md — 오케스트레이터 커맨드 (핵심)

**Files:**
- Create: `plugins/trading-analyst/commands/analyze.md`

- [ ] **Step 1: 파일 작성**

`plugins/trading-analyst/commands/analyze.md`:

````markdown
---
description: 미국 주식 종목 다중 에이전트 분석 — BUY/HOLD/SELL 결론 도출
---

# 주식 종목 분석

분석 종목: **$ARGUMENTS**

아래 파이프라인을 단계별로 실행하세요.

---

## Step 1: 데이터 수집

다음 명령을 실행하여 JSON 데이터를 수집합니다:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/tools/fetch_data.py $ARGUMENTS
```

JSON 결과를 `STOCK_DATA` 변수로 저장해두세요. 오류 발생 시 사용자에게 알리고 중단합니다.

---

## Step 2: 병렬 분석 (3개 에이전트 동시 실행)

다음 3개 에이전트를 **Agent 툴로 동시에** 소환합니다. 모두 완료될 때까지 기다린 후 다음 단계로 넘어갑니다.

### Agent A — 기술적 분석가

**프롬프트:**
```
당신은 경험 많은 기술적 분석 전문가입니다.
아래 주식 데이터를 분석하고 기술적 관점에서 투자 의견을 제시하세요.

[데이터]
{STOCK_DATA의 ticker, price, technicals 섹션}

[분석 요구사항]
1. RSI 해석 (과매수/과매도/중립)
2. MACD 신호 해석
3. 50일선, 200일선 대비 현재가 위치
4. 거래량 분석 (volume_ratio)
5. 단기/중기 기술적 추세 판단

[출력 형식]
- 기술적 종합 의견: BULLISH / NEUTRAL / BEARISH
- 핵심 근거 3가지 (각 한 줄)
- 주목할 지지/저항 레벨
```

### Agent B — 펀더멘털 분석가

**프롬프트:**
```
당신은 CFA 자격증을 보유한 펀더멘털 분석 전문가입니다.
아래 주식 데이터를 분석하고 펀더멘털 관점에서 투자 의견을 제시하세요.

[데이터]
{STOCK_DATA의 ticker, fundamentals 섹션}

[분석 요구사항]
1. 밸류에이션 평가 (PER, Forward PER — 섹터/시장 대비)
2. 수익성 분석 (EPS, 이익률)
3. 성장성 평가 (매출 성장률)
4. 재무 건전성 (부채비율)
5. 시가총액 규모 및 섹터 특성

[출력 형식]
- 펀더멘털 종합 의견: STRONG / FAIR / WEAK
- 핵심 근거 3가지 (각 한 줄)
- 주요 리스크 요인 1가지
```

### Agent C — 뉴스/감성 분석가

**프롬프트:**
```
당신은 금융 뉴스 분석 전문가입니다.
아래 헤드라인과 추가 검색을 통해 현재 시장 감성을 분석하세요.

[수집된 헤드라인]
{STOCK_DATA의 ticker, news_headlines 섹션}

[추가 검색 지시]
WebSearch 툴로 다음을 검색하세요:
- "{ticker} stock news 2026"
- "{ticker} earnings analyst forecast"

[분석 요구사항]
1. 최근 주요 뉴스 카탈리스트
2. 애널리스트 컨센서스 (있는 경우)
3. 시장 감성 (긍정/중립/부정)
4. 단기 리스크 요인

[출력 형식]
- 뉴스/감성 종합 의견: POSITIVE / NEUTRAL / NEGATIVE
- 핵심 뉴스 3가지 (각 한 줄)
- 주목할 리스크 1가지
```

---

## Step 3: Bull Researcher

Agent A, B, C의 결과를 모아 다음 에이전트를 소환합니다.

**프롬프트:**
```
당신은 강세론을 주장하는 투자 리서처입니다.
아래 분석 자료를 바탕으로 {ticker} 매수를 지지하는 가장 강력한 논거를 구성하세요.

[기술적 분석 결과]
{Agent A 결과}

[펀더멘털 분석 결과]
{Agent B 결과}

[뉴스/감성 분석 결과]
{Agent C 결과}

[요구사항]
- 매수를 지지하는 핵심 논거 3가지
- 각 논거의 구체적 데이터 근거
- 목표가 또는 상승 여력 추정 (가능하면)
- 단기(1개월), 중기(6개월) 관점 구분

형식: 간결하고 설득력 있게, 총 200단어 이내
```

---

## Step 4: Bear Researcher

**프롬프트:**
```
당신은 약세론을 주장하는 투자 리서처입니다.
아래 분석 자료와 강세 논거를 반박하는 논거를 구성하세요.

[기술적 분석 결과]
{Agent A 결과}

[펀더멘털 분석 결과]
{Agent B 결과}

[뉴스/감성 분석 결과]
{Agent C 결과}

[강세론 논거]
{Step 3 결과}

[요구사항]
- 매도/관망을 지지하는 핵심 논거 3가지
- 강세론의 약점 지적
- 주요 하방 리스크 요인
- 단기(1개월), 중기(6개월) 관점 구분

형식: 간결하고 설득력 있게, 총 200단어 이내
```

---

## Step 5: Research Manager

**프롬프트:**
```
당신은 시니어 리서치 매니저입니다.
강세론과 약세론을 균형 있게 검토하고 핵심 투자 포인트를 정리하세요.

[전체 분석 데이터]
종목: {ticker}
현재가: {current price}

[기술적 분석] {Agent A 결과}
[펀더멘털 분석] {Agent B 결과}
[뉴스/감성] {Agent C 결과}
[강세 논거] {Step 3 결과}
[약세 논거] {Step 4 결과}

[요구사항]
1. 양측 논거의 핵심 쟁점 2-3가지 정리
2. 어느 측 논거가 더 설득력 있는지와 그 이유
3. 최종 판단에서 가장 중요한 변수 1가지
4. 불확실성 수준: HIGH / MEDIUM / LOW

형식: 총 150단어 이내
```

---

## Step 6: Portfolio Manager (최종 결정)

**프롬프트:**
```
당신은 최종 투자 결정권을 가진 포트폴리오 매니저입니다.
모든 분석을 종합해 명확한 투자 결정을 내리세요.

[종합 분석 패키지]
종목: {ticker} | 날짜: {date} | 현재가: {current price}

{Research Manager 요약}
{기술적: bullish/neutral/bearish}
{펀더멘털: strong/fair/weak}
{뉴스/감성: positive/neutral/negative}

[결정 요구사항]
1. 투자 결정: BUY / HOLD / SELL (반드시 셋 중 하나)
2. 신뢰도: 0-100% (숫자만)
3. 결정 근거: 2-3문장
4. 주요 리스크: 1문장
5. 모니터링 포인트: 1가지

[출력 형식 — 반드시 이 형식으로]
DECISION: [BUY/HOLD/SELL]
CONFIDENCE: [숫자]%
RATIONALE: [2-3문장]
RISK: [1문장]
WATCH: [1가지]
```

---

## Step 7: 최종 출력

모든 에이전트 결과를 수집해 아래 형식으로 터미널에 출력합니다:

```
══════════════════════════════════════════════════
  {TICKER} 종합 분석  |  {DATE}  |  현재가 ${PRICE}
══════════════════════════════════════════════════

 결론: {BUY/HOLD/SELL}  (신뢰도: {CONFIDENCE}%)

──────────────────────────────────────────────────
 📈 기술적 분석  [{BULLISH/NEUTRAL/BEARISH}]
    {기술적 핵심 근거 3줄}

 📊 펀더멘털 분석  [{STRONG/FAIR/WEAK}]
    {펀더멘털 핵심 근거 3줄}

 📰 뉴스/감성  [{POSITIVE/NEUTRAL/NEGATIVE}]
    {뉴스 핵심 3줄}

 🐂 강세 논거
    {Bull 핵심 포인트 2줄}

 🐻 약세 논거
    {Bear 핵심 포인트 2줄}

 ⚖️  종합 판단
    {RATIONALE}

 ⚠️  주요 리스크
    {RISK}

 👀 모니터링 포인트
    {WATCH}

══════════════════════════════════════════════════
 면책고지: 본 분석은 AI가 생성한 참고 정보이며
 실제 투자 결정의 책임은 투자자 본인에게 있습니다.
══════════════════════════════════════════════════
```
````

- [ ] **Step 2: 커밋**

```bash
cd /home/seoji/jhseo-plugin
git add plugins/trading-analyst/commands/analyze.md
git commit -m "feat: add analyze.md orchestrator command"
```

---

## Task 5: marketplace.json 업데이트

**Files:**
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: plugins 배열에 trading-analyst 추가**

`.claude-plugin/marketplace.json`의 `plugins` 배열에 아래 항목을 추가:

```json
{
  "name": "trading-analyst",
  "source": "./plugins/trading-analyst",
  "description": "미국 주식 다중 에이전트 분석. /analyze <TICKER>로 BUY/HOLD/SELL 결론 도출",
  "version": "1.0.0",
  "author": {
    "name": "JiHyeong Seo"
  },
  "keywords": ["trading", "stock", "analysis", "finance", "미국주식", "주식분석"],
  "category": "finance"
}
```

최종 파일 전체:

```json
{
  "name": "jhseo-plugins",
  "owner": {
    "name": "JiHyeong Seo",
    "email": "seojihyeong@nexon.co.kr"
  },
  "metadata": {
    "description": "JiHyeong Seo의 개인 Claude Code 플러그인 모음"
  },
  "plugins": [
    {
      "name": "session-manager",
      "source": "./plugins/session-manager",
      "description": "Claude Code 세션 브라우저. 멀티슬롯 tmux 패널, fzf 검색, resume/삭제 관리",
      "version": "2.0.3",
      "author": {
        "name": "JiHyeong Seo"
      },
      "keywords": ["session", "resume", "browser", "fzf", "tmux", "세션", "세션관리"],
      "category": "productivity"
    },
    {
      "name": "trading-analyst",
      "source": "./plugins/trading-analyst",
      "description": "미국 주식 다중 에이전트 분석. /analyze <TICKER>로 BUY/HOLD/SELL 결론 도출",
      "version": "1.0.0",
      "author": {
        "name": "JiHyeong Seo"
      },
      "keywords": ["trading", "stock", "analysis", "finance", "미국주식", "주식분석"],
      "category": "finance"
    }
  ]
}
```

- [ ] **Step 2: 커밋**

```bash
cd /home/seoji/jhseo-plugin
git add .claude-plugin/marketplace.json
git commit -m "feat: register trading-analyst in marketplace.json"
```

---

## Task 6: yfinance 설치 확인 및 통합 검증

- [ ] **Step 1: 의존성 설치 확인**

```bash
python3 -c "import yfinance; import pandas; print('OK')"
```

설치 안 되어 있으면:
```bash
pip install yfinance pandas
```

- [ ] **Step 2: fetch_data.py 실제 동작 확인**

```bash
cd /home/seoji/jhseo-plugin
python plugins/trading-analyst/tools/fetch_data.py NVDA
```

Expected: JSON 출력, 모든 필드 존재

- [ ] **Step 3: 전체 테스트 실행**

```bash
cd /home/seoji/jhseo-plugin
python -m pytest tests/test_fetch_data.py -v
```

Expected: 모든 테스트 PASS

- [ ] **Step 4: 플러그인 구조 최종 확인**

```bash
find /home/seoji/jhseo-plugin/plugins/trading-analyst -type f | sort
```

Expected:
```
plugins/trading-analyst/.claude-plugin/plugin.json
plugins/trading-analyst/SKILL.md
plugins/trading-analyst/commands/analyze.md
plugins/trading-analyst/tools/fetch_data.py
```

- [ ] **Step 5: 최종 커밋**

```bash
cd /home/seoji/jhseo-plugin
git add .
git commit -m "chore: verify trading-analyst plugin structure complete"
```
