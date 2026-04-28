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
