# Trading Analyst Plugin — Design Spec

**Date:** 2026-04-28
**Status:** Approved

---

## Overview

미국 주식 종목을 Claude Code 슬래시 커맨드 하나로 분석하는 플러그인.
TradingAgents 오픈소스의 다중 에이전트 파이프라인을 Claude Code subagents로 재구현하여,
별도 Anthropic API 키 비용 없이 구독 안에서 전체 분석을 수행한다.

**커맨드:** `/analyze <TICKER>` (예: `/analyze NVDA`)
**출력:** 터미널 텍스트 (BUY / HOLD / SELL + 신뢰도 + 근거 요약)
**소요 시간:** 약 3~5분

---

## 파일 구조

```
plugins/trading-analyst/
├── .claude-plugin/
│   └── plugin.json          # 플러그인 메타데이터
├── SKILL.md                 # 플러그인 소개 및 사용법
├── commands/
│   └── analyze.md           # /analyze 슬래시 커맨드 오케스트레이터
└── tools/
    └── fetch_data.py        # yfinance 데이터 수집기 (추후 유료 API 교체 가능)
```

---

## 에이전트 파이프라인

```
/analyze <TICKER>
    │
    ① fetch_data.py 실행
    │  → 주가, 기술지표, 재무제표, 최근 뉴스 헤드라인 수집 (yfinance)
    │  → JSON 형태로 반환
    │
    ② [병렬 subagents]
    │  ├── 기술적 분석 Agent   (price + technicals)
    │  ├── 펀더멘털 분석 Agent (fundamentals)
    │  └── 뉴스/감성 Agent    (news_headlines + WebSearch 실시간 검색)
    │
    ③ [순차]
    │  ├── Bull Researcher Agent  (강세 근거 수립)
    │  └── Bear Researcher Agent  (약세 근거 수립)
    │
    ④ Research Manager Agent
    │  → Bull/Bear 토론 종합, 핵심 쟁점 정리
    │
    ⑤ Portfolio Manager Agent
       → 최종 BUY / HOLD / SELL 결정 + 신뢰도(%) + 근거 요약
```

---

## 데이터 흐름

### fetch_data.py 출력 스키마

```json
{
  "ticker": "NVDA",
  "date": "2026-04-28",
  "price": {
    "current": 875.4,
    "change_1d": 2.3,
    "change_1w": -1.2,
    "change_1m": 8.5
  },
  "technicals": {
    "rsi": 62,
    "macd": "bullish",
    "ma50": 820,
    "ma200": 750,
    "volume_ratio": 1.2
  },
  "fundamentals": {
    "pe": 45.2,
    "eps": 19.4,
    "revenue_growth_yoy": "122%",
    "debt_equity": 0.4,
    "market_cap": "2.1T"
  },
  "news_headlines": [
    "NVDA beats Q1 estimates by 15%",
    "AI chip demand expected to surge in H2"
  ]
}
```

### 에이전트 입력 매핑

| 에이전트 | 입력 |
|---|---|
| 기술적 분석 | `price` + `technicals` |
| 펀더멘털 분석 | `fundamentals` |
| 뉴스/감성 | `news_headlines` + WebSearch |
| Bull/Bear Researcher | 위 3개 에이전트 결과 전체 |
| Research Manager | Bull + Bear 결과 |
| Portfolio Manager | Research Manager 결과 + 전체 데이터 |

---

## 최종 출력 형태

```
══════════════════════════════════════════════
  NVDA 종합 분석  |  2026-04-28
══════════════════════════════════════════════
 결론: BUY  (신뢰도: 78%)
──────────────────────────────────────────────
 📈 기술적 분석
    RSI 62 (중립~강세), MACD 골든크로스 진입
    50일선 지지 확인, 거래량 평균 대비 1.2배

 📊 펀더멘털 분석
    PER 45.2 — AI 섹터 평균(52) 대비 적정
    YoY 매출 성장 122%, 부채비율 낮음

 📰 뉴스/감성
    Q1 어닝 서프라이즈, AI 수요 모멘텀 긍정적
    단기 수출 규제 리스크 존재

 🐂 강세 근거
    AI 인프라 투자 사이클 초입, 독점적 CUDA 생태계

 🐻 약세 근거
    밸류에이션 부담, 지정학적 리스크, 경쟁사 추격

 ⚖️  종합 판단
    단기 모멘텀과 장기 펀더멘털 모두 긍정적.
    리스크 대비 기대수익 우위 — BUY 권고.
══════════════════════════════════════════════
```

---

## 확장성

### 추후 유료 API 연동 (C 옵션)

`fetch_data.py`는 provider 패턴으로 설계되어, `.env`에 키 추가만으로 데이터 소스 교체 가능.

```bash
FINNHUB_API_KEY=xxx        # 뉴스/감성 데이터 업그레이드
ALPHA_VANTAGE_KEY=xxx      # 기술지표 업그레이드
```

환경변수 존재 여부에 따라 자동으로 더 풍부한 데이터 소스를 선택한다.

---

## 제약사항

- yfinance는 15분 지연 데이터 (장중 실시간 아님)
- WebSearch 결과 품질은 검색 타이밍에 의존
- 전체 분석 소요 시간 약 3~5분
- Claude Code Max 플랜 기준 subagent 비용 없음

---

## marketplace.json 등록

기존 `session-manager`와 동일한 패턴으로 플러그인 목록에 추가.

```json
{
  "name": "trading-analyst",
  "source": "./plugins/trading-analyst",
  "description": "미국 주식 종목 다중 에이전트 분석. /analyze <TICKER>로 BUY/HOLD/SELL 결론 도출",
  "version": "1.0.0",
  "keywords": ["trading", "stock", "analysis", "finance", "미국주식"],
  "category": "finance"
}
```
