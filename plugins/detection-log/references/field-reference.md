# Detection Log Field Reference

## ES 인덱스 정보

- 인덱스 패턴: `engagement-api-http-access-log-*`
- 일별 인덱스: `engagement-api-http-access-log-YYYY.MM.DD`
- 엔드포인트: `https://apik.plex.nexon.io:5502`
- 텍스트탐지, 이미지탐지 API 로그 모두 동일 인덱스에 적재

## 주요 필드

### Request 필드

| 필드 경로 | 타입 | 설명 |
|-----------|------|------|
| `request.path` | keyword | API 엔드포인트 (`/inference/textclassifier`, `/inference/textclassifier_big`) |
| `request.body.serviceId` | keyword | 호출 서비스 식별자 |
| `request.body.serviceType` | integer | 서비스 타입 |
| `request.body.types` | keyword[] | 요청한 탐지 모델 배열 |
| `request.body.data.text` | text[] | 입력 텍스트 배열 |
| `request.body.data.len` | integer | 입력 텍스트 배열 길이 |
| `request.body.data.text_len` | integer[] | 각 텍스트의 문자 길이 |
| `request.headers.x-inface-api-key` | keyword | 사용자 API 키 (inface GW 경유 시) |
| `request.headers.x-envoy-original-path` | keyword | GW 원본 경로 (리전 판별용) |
| `request.headers.x-inface-gw-env` | keyword | GW 환경 (live/stage 등) |
| `request.headers.x-inface-real-ip` | keyword | 실제 클라이언트 IP |

### Response / 처리 필드

| 필드 경로 | 타입 | 설명 |
|-----------|------|------|
| `@timestamp` | date | 로그 타임스탬프 |
| `timestamp` | string | 로그 타임스탬프 (문자열) |
| `response.status` | integer | HTTP 응답 상태 코드 |
| `process_time` | integer | 처리 시간 (ms) |
| `region` | keyword | 서버 리전 (예: ap-northeast-1) |
| `level_name` | keyword | 로그 레벨 (INFO 등) |
| `log_type` | keyword | 로그 타입 (`engagement-api-http-access-log`) |

### Stat 필드 (모델별 탐지 결과)

`stat` 하위에 모델명으로 중첩된 구조:

| 필드 | 타입 | 설명 |
|------|------|------|
| `stat.{model}.infer_detect` | integer | 탐지 건수 (prediction 중 0.8 이상인 값의 수) |
| `stat.{model}.infer_prediction` | float[] | 모델 예측값 배열 (0~1 사이, 0.8 이상이면 탐지) |
| `stat.{model}.infer_count` | integer | 추론 대상 수 (= request.body.data.len) |

예시: `stat.badword_kor.infer_detect`, `stat.ad_global.infer_prediction`

## 탐지 타입 분류

### AI 모델

| 타입 | 설명 |
|------|------|
| `badnick_kor` | 유해 닉네임 - 한국어 |
| `badnick_en` | 유해 닉네임 - 영어 |
| `badword_kor` | 유해 표현 - 한국어 |
| `badword_eng` | 유해 표현 - 영어 |
| `badword_jpn` | 유해 표현 - 일본어 |
| `badword_chn` | 유해 표현 - 중국어(간체) |
| `badword_twn` | 유해 표현 - 대만(번체) |
| `badword_thi` | 유해 표현 - 태국어 |
| `ad_global` | 광고성 표현 - 글로벌 |
| `ad_kor` | 광고성 표현 - 한국어 |
| `sexual_kor` | 외설 표현 - 한국어 |
| `sentiment_kor` | 감성 분석 - 한국어 |
| `sentiment_eng` | 감성 분석 - 영어 (beta) |
| `sentiment_jpn` | 감성 분석 - 일본어 (beta) |

### BWS (금칙어) 타입

| 타입 | 설명 |
|------|------|
| `restricted_word` | 금칙어 부분 일치 - 게임 내 채팅, 게시물 |
| `restricted_word#blacklist` | 금칙어 완전 일치 |
| `reserved_word` | 예약어 부분 일치 - 닉네임, 월드명, 길드명 |
| `reserved_word#blacklist` | 예약어 완전 일치 |
| `livechat_restricted_word` | 라이브채팅 금칙어 부분 일치 |
| `livechat_restricted_word#blacklist` | 라이브채팅 금칙어 완전 일치 |
| `restricted_chn` | 중국 정부 금칙어 |

BWS 타입은 `#언어코드` 접미사 가능 (기본값: ko):
- `restricted_word` = `restricted_word#ko`
- `restricted_word#blacklist#en`
- `reserved_word#blacklist#de`
- `restricted_word#global`

## 리전 매핑

| x-envoy-original-path 패턴 | 리전 | CLI 코드 |
|-----------------------------|------|----------|
| `/inference/textclassifier` | Seoul (기본) | `seoul` |
| `/inference/tyo/textclassifier` | Tokyo | `tokyo` |
| `/inference/hkg/textclassifier` | HongKong | `hongkong` |
| `/inference/org/textclassifier` | Oregon | `oregon` |
| `/inference/sin/textclassifier` | Singapore | `singapore` |
| `/inference/fra/textclassifier` | Frankfurt | `frankfurt` |

`textclassifier_big` 변형도 동일 리전 매핑 적용.

## API 호출 URL 매핑

| URL | 리전 |
|-----|------|
| `https://private-apn2.api.nexon.com/inference/textclassifier` | Seoul |
| `https://private-apn1.api.nexon.com/inference/tyo/textclassifier` | Tokyo |
| `https://private-ape1.api.nexon.com/inference/hkg/textclassifier` | HongKong |
| `https://private-usw2.api.nexon.com/inference/org/textclassifier` | Oregon |
| `https://private-apse1.api.nexon.com/inference/sin/textclassifier` | Singapore |
| `https://private-euc1.api.nexon.com/inference/fra/textclassifier` | Frankfurt |
