---
name: confluence
description: Confluence 페이지 검색/조회/생성/수정. "confluence", "컨플루언스", "컨플", "문서 생성", "페이지 검색", "배포 노트" 등의 키워드에서 활성화
---

# Confluence 스킬

Confluence 페이지를 검색, 조회, 생성, 수정하는 스킬입니다.

## 트리거

다음 키워드가 포함된 요청에서 활성화됩니다:
- "confluence", "컨플루언스", "컨플"
- "문서 생성", "페이지 생성", "페이지 만들"
- "페이지 검색", "문서 검색"
- "배포 문서", "배포 노트", "패치 노트"

## 환경 설정

**필수 환경변수:**
```bash
export CONFLUENCE_API_TOKEN="your-bearer-token"
```

## 허용 범위

- **공간(Space):** NAD (플랫폼 본부 스페이스)
- **페이지:** 2674833208 (유해탐지팀 컨플 문서 최상단) 및 그 하위 페이지만

사용자에게 응답할 때:
- 'NAD' 대신 '플랫폼 본부'
- '2674833208' 대신 '유해탐지팀 컨플 문서'라고 표현하세요.

## 서비스·레포 매핑

| 레포지토리 | 서비스명 |
|------------|----------|
| engagement_api_fastapi | 텍스트탐지 API |
| engagement_image_detect_fastapi | 이미지탐지 API |
| clean-chatbot/api | 클린챗봇 백엔드 |
| clean-chatbot/front-new | 클린챗봇 프론트 |
| bws/console-backend, console-front, db-server | 통합 차단어(BWS) |

## 문서 작성 전 확인사항

페이지를 생성하기 전에 반드시 사용자에게 확인:
1. 배포할 공간(또는 부모 페이지 위치)
2. 배포할 내용(제목/개요)

## API 사용 방법 (Python CLI)

CLI 경로: `${CLAUDE_PLUGIN_ROOT}/confluence.py`

### 페이지 검색
```bash
python ${CLAUDE_PLUGIN_ROOT}/confluence.py search "검색어"
python ${CLAUDE_PLUGIN_ROOT}/confluence.py search "검색어" -s NAD -l 10
```

### 페이지 조회
```bash
python ${CLAUDE_PLUGIN_ROOT}/confluence.py get {pageId}
```

### 페이지 트리 조회
```bash
python ${CLAUDE_PLUGIN_ROOT}/confluence.py tree
```

### 페이지 생성
```bash
python ${CLAUDE_PLUGIN_ROOT}/confluence.py create -t "제목" -c "<p>내용</p>" -p "부모페이지ID"
```

### 페이지 수정
```bash
python ${CLAUDE_PLUGIN_ROOT}/confluence.py update {pageId} -t "새 제목" -c "<p>새 내용</p>"
```

## 배포 노트 컨벤션

배포/패치 노트 작성 시:
1. **제목 형식:** `(YYYY/MM/DD) 개요`
   - 날짜는 슬래시 형식 (예: 2026/01/29)
   - summary에는 환경([개발] 등), 버전 접두어 넣지 않고 개요만
2. **본문:** deployment 템플릿 사용
   - 템플릿 변수(배포 일시, 버전, 담당자, 변경 사항, 배포 절차 등)를 채워 넣어 템플릿 구조 준수

## 참조 문서

스타일 가이드 및 템플릿은 references/ 폴더를 참고하세요:
- `references/api-reference.md` - API 엔드포인트 상세
- `references/style-guide.md` - Confluence 문서 스타일 가이드
- `references/templates/` - 문서 템플릿들
