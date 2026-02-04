# 배포 노트 템플릿

이 템플릿은 배포 노트 문서 생성 시 참고용입니다.

## 1. 배포 정보

| 항목 | 내용 |
|------|------|
| 서비스 | {service_name} |
| 배포 환경 | {environment} |
| 배포 버전 | {version} |
| 배포 일시 | {deploy_date} |
| 배포 태그 | `{tag}` |
| 담당자 | {deployer} |

## 2. 변경 사항

### 2.1 Commit 히스토리

| Hash | Author | Date | Message |
|------|--------|------|---------|
{commit_history}

### 2.2 변경된 파일

#### 추가된 파일 ({added_count}개)
{added_files}

#### 수정된 파일 ({modified_count}개)
{modified_files}

#### 삭제된 파일 ({deleted_count}개)
{deleted_files}

## 3. 배포 절차

### 3.1 배포 전 체크리스트

- [ ] 코드 리뷰 완료
- [ ] 테스트 통과 확인
- [ ] 데이터베이스 마이그레이션 검토
- [ ] 의존성 변경 사항 확인
- [ ] 설정 파일 업데이트 확인
- [ ] 모니터링 및 알림 설정 확인

### 3.2 배포 명령어

```bash
# 태그 체크아웃
git checkout {tag}

# 의존성 설치
pip install -r requirements.txt

# 배포 스크립트 실행
./deploy.sh {environment}
```

### 3.3 배포 후 검증

- [ ] 서비스 Health Check (GET /health)
- [ ] API 응답 확인 (주요 엔드포인트 테스트)
- [ ] 로그 확인 (에러 로그 모니터링)
- [ ] 모니터링 지표 확인 (CPU, Memory, Request Count)
- [ ] 데이터베이스 연결 확인
- [ ] 외부 API 연동 확인

## 4. 롤백 계획

### 4.1 롤백 시나리오

다음 상황 발생 시 즉시 롤백:
- 서비스 전체 장애 발생
- 심각한 버그로 인한 데이터 손실 위험
- 성능 저하 (응답 시간 2배 이상 증가)
- 에러율 급증 (5% 이상)

### 4.2 롤백 명령어

```bash
# 이전 버전으로 롤백
git checkout {prev_tag}

# 배포 스크립트 실행
./deploy.sh {environment}

# 서비스 재시작
systemctl restart {service_name}
```

### 4.3 롤백 후 조치

- [ ] 롤백 사유 문서화
- [ ] 버그 수정 계획 수립
- [ ] 재배포 일정 협의

## 5. 참고 사항

### 5.1 관련 문서
- [이전 배포 노트](link)
- [서비스 운영 가이드](link)

### 5.2 관련 이슈
-

### 5.3 특이 사항
-
