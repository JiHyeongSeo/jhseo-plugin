#!/usr/bin/env python3
"""Deployment Notes CLI - Git 태그 기반 배포 노트 자동 생성"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 환경 변수
def get_confluence_cli_path() -> str:
    """Confluence CLI 경로 찾기"""
    # 1. 환경 변수 확인
    if "CONFLUENCE_CLI_PATH" in os.environ:
        return os.environ["CONFLUENCE_CLI_PATH"]

    # 2. Claude plugin cache 확인
    home = os.path.expanduser("~")
    cache_path = os.path.join(home, ".claude", "plugins", "cache", "sol-plugins", "confluence")
    if os.path.exists(cache_path):
        # 최신 버전 찾기
        versions = [d for d in os.listdir(cache_path) if os.path.isdir(os.path.join(cache_path, d))]
        if versions:
            versions.sort(reverse=True)
            cli_path = os.path.join(cache_path, versions[0], "confluence.py")
            if os.path.exists(cli_path):
                return cli_path

    # 3. 상대 경로 (개발 환경)
    relative_path = os.path.join(os.path.dirname(__file__), "..", "confluence", "confluence.py")
    if os.path.exists(relative_path):
        return relative_path

    raise FileNotFoundError("Confluence CLI를 찾을 수 없습니다. CONFLUENCE_CLI_PATH 환경 변수를 설정하세요.")


CONFLUENCE_CLI = get_confluence_cli_path()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

# 레포지토리별 설정
REPO_CONFIG = {
    "engagement_api_fastapi": {
        "service_name": "텍스트/이미지탐지 API",
        "patch_notes_page_id": "1719919196",  # "텍스트/이미지 탐지 API 패치노트" 페이지
        "release_notes_page_id": None,  # "상세 릴리즈 노트" 페이지 (자동 생성 또는 검색)
    }
}

# 환경 매핑
ENV_MAPPING = {
    "dev": "개발",
    "stage": "스테이징",
    "prod": "운영",
}


def run_command(cmd: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    """명령어 실행"""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def parse_tag(tag: str) -> Optional[Dict[str, str]]:
    """
    태그 형식 파싱: {환경}-v{버전}
    예: dev-v1.2.3 -> {"env": "dev", "version": "1.2.3"}
    """
    pattern = r"^(dev|stage|prod)-v(\d+\.\d+\.\d+)$"
    match = re.match(pattern, tag)
    if not match:
        return None
    return {"env": match.group(1), "version": match.group(2)}


def get_repo_name() -> Optional[str]:
    """현재 레포지토리 이름 가져오기"""
    code, stdout, _ = run_command(["git", "rev-parse", "--show-toplevel"])
    if code != 0:
        return None
    return Path(stdout).name


def get_prev_tag(current_tag: str, env: str) -> Optional[str]:
    """이전 배포 태그 찾기 (같은 환경)"""
    code, stdout, _ = run_command(["git", "tag", "--sort=-version:refname"])
    if code != 0:
        return None

    tags = [t for t in stdout.split("\n") if t]
    found_current = False

    for tag in tags:
        if tag == current_tag:
            found_current = True
            continue
        if found_current:
            parsed = parse_tag(tag)
            if parsed and parsed["env"] == env:
                return tag
    return None


def get_commits(from_tag: Optional[str], to_tag: str) -> List[Dict[str, str]]:
    """커밋 히스토리 가져오기"""
    if from_tag:
        cmd = ["git", "log", f"{from_tag}..{to_tag}", "--pretty=format:%H|%an|%ae|%ai|%s"]
    else:
        cmd = ["git", "log", to_tag, "--pretty=format:%H|%an|%ae|%ai|%s"]

    code, stdout, _ = run_command(cmd)
    if code != 0:
        return []

    commits = []
    for line in stdout.split("\n"):
        if not line:
            continue
        parts = line.split("|", 4)
        if len(parts) == 5:
            commits.append({
                "hash": parts[0][:7],
                "author": parts[1],
                "email": parts[2],
                "date": parts[3],
                "message": parts[4],
            })
    return commits


def get_file_changes(from_tag: Optional[str], to_tag: str) -> Dict[str, List[Dict[str, str]]]:
    """파일 변경 목록 가져오기"""
    if from_tag:
        cmd = ["git", "diff", "--numstat", from_tag, to_tag]
    else:
        cmd = ["git", "diff", "--numstat", "4b825dc642cb6eb9a060e54bf8d69288fbee4904", to_tag]  # empty tree

    code, stdout, _ = run_command(cmd)
    if code != 0:
        return {"added": [], "modified": [], "deleted": []}

    changes = {"added": [], "modified": [], "deleted": []}

    for line in stdout.split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue

        added, deleted, path = parts[0], parts[1], parts[2]

        if added == "-" and deleted == "-":
            # Binary file
            changes["modified"].append({"path": path, "type": "binary"})
        elif added != "0" and deleted == "0":
            changes["added"].append({"path": path, "added": added})
        elif added == "0" and deleted != "0":
            changes["deleted"].append({"path": path, "deleted": deleted})
        else:
            changes["modified"].append({"path": path, "added": added, "deleted": deleted})

    return changes


def get_tag_date(tag: str) -> str:
    """태그 생성 날짜 가져오기"""
    code, stdout, _ = run_command(["git", "log", "-1", "--format=%ai", tag])
    if code != 0:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return stdout


def load_template() -> str:
    """배포 노트 템플릿 로드"""
    template_path = os.path.join(TEMPLATE_DIR, "deployment-template.md")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def search_confluence(query: str) -> Dict:
    """Confluence에서 페이지 검색"""
    cmd = ["python3", CONFLUENCE_CLI, "search", query, "-l", "10"]
    code, stdout, stderr = run_command(cmd)

    if code != 0:
        return {"error": f"Search failed: {stderr}"}

    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON response: {stdout}"}


def get_confluence_page(page_id: str) -> Dict:
    """Confluence 페이지 조회"""
    cmd = ["python3", CONFLUENCE_CLI, "get", page_id]
    code, stdout, stderr = run_command(cmd)

    if code != 0:
        return {"error": f"Get page failed: {stderr}"}

    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON response: {stdout}"}


def update_confluence_page(page_id: str, title: Optional[str] = None, content: Optional[str] = None) -> Dict:
    """Confluence 페이지 업데이트"""
    cmd = ["python3", CONFLUENCE_CLI, "update", page_id]

    if title:
        cmd.extend(["-t", title])
    if content:
        cmd.extend(["-c", content])

    code, stdout, stderr = run_command(cmd)

    if code != 0:
        return {"error": f"Update page failed: {stderr}"}

    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON response: {stdout}"}


def search_version_document(version: str, parent_page_id: str, doc_type: str = "patch") -> Optional[str]:
    """버전별 문서가 이미 존재하는지 검색

    Args:
        version: 버전 번호 (예: "1.2.3")
        parent_page_id: 부모 페이지 ID
        doc_type: "patch" 또는 "release"

    Returns:
        페이지 ID (존재하면) 또는 None
    """
    if doc_type == "patch":
        search_query = f"v{version}"
    else:
        search_query = f"v{version} 릴리즈 노트"

    result = search_confluence(search_query)

    if result.get("total", 0) > 0:
        pages = result.get("pages", [])
        for page in pages:
            # 정확한 버전 매칭 (v{version}으로 시작하는지 확인)
            if doc_type == "patch":
                # 패치노트: "(YYYY/MM/DD) v{version}" 형식
                if f"v{version}" in page["title"]:
                    return page["id"]
            else:
                # 릴리즈 노트: "v{version} 릴리즈 노트" 형식
                if page["title"] == f"v{version} 릴리즈 노트":
                    return page["id"]

    return None


def generate_summary_from_commits(commits: List[Dict[str, str]]) -> str:
    """커밋 메시지에서 요약 생성 (첫 커밋 메시지 활용)"""
    if not commits:
        return "배포"

    # 첫 번째 커밋 메시지 사용
    first_commit = commits[0]["message"]

    # 최대 50자로 제한
    if len(first_commit) > 50:
        return first_commit[:47] + "..."

    return first_commit


def update_deployment_history(page_id: str, env: str, env_kr: str, tag_date: str) -> Dict:
    """문서의 배포 이력 섹션 업데이트"""
    # 기존 페이지 내용 가져오기
    page = get_confluence_page(page_id)
    if "error" in page:
        return page

    content = page.get("content", "")

    # 배포 이력 테이블 찾기
    import re
    history_pattern = r'<h2>배포 이력</h2>.*?<table>(.*?)</table>'
    match = re.search(history_pattern, content, re.DOTALL)

    new_row = f"<tr><td>{env_kr} ({env})</td><td>{tag_date}</td></tr>\n"

    if match:
        # 기존 테이블에 행 추가 (중복 확인)
        table_content = match.group(1)
        if env in table_content:
            # 이미 해당 환경이 있으면 업데이트
            env_pattern = rf'<tr><td>{env_kr} \({env}\)</td><td>.*?</td></tr>'
            table_content = re.sub(env_pattern, new_row.strip(), table_content)
        else:
            # 새로운 환경 추가
            table_content += new_row

        # 테이블 교체
        new_table = f"<table>\n{table_content}</table>"
        content = re.sub(history_pattern, f'<h2>배포 이력</h2>\n{new_table}', content, flags=re.DOTALL)
    else:
        # 배포 이력 섹션이 없으면 추가
        history_section = f"""<h2>배포 이력</h2>
<table>
<tr><th>환경</th><th>배포 일시</th></tr>
{new_row}
</table>
"""
        # 첫 번째 h2 섹션 앞에 추가
        first_h2 = content.find("<h2>")
        if first_h2 != -1:
            content = content[:first_h2] + history_section + content[first_h2:]
        else:
            content = history_section + content

    # 페이지 업데이트
    return update_confluence_page(page_id, content=content)


def find_or_create_release_notes_page(patch_notes_page_id: str, service_name: str, interactive: bool = True) -> Optional[str]:
    """상세 릴리즈 노트 페이지 찾거나 생성"""
    # 1. 먼저 검색
    search_result = search_confluence(f"{service_name} 상세 릴리즈 노트")

    if search_result.get("total", 0) > 0:
        pages = search_result.get("pages", [])
        if pages:
            page = pages[0]
            if interactive:
                print(f"\n찾은 페이지: {page['title']} (ID: {page['id']})")
                print(f"URL: {page['url']}")
                response = input("이 페이지를 사용하시겠습니까? (y/n): ")
                if response.lower() == 'y':
                    return page['id']
            else:
                return page['id']

    # 2. 없으면 생성 제안
    if interactive:
        print(f"\n'{service_name} 상세 릴리즈 노트' 페이지가 없습니다.")
        print(f"패치노트 페이지 하위에 생성하시겠습니까?")
        response = input("생성하시겠습니까? (y/n): ")
        if response.lower() != 'y':
            return None

    # 3. 페이지 생성
    title = f"{service_name} 상세 릴리즈 노트"
    content = f"""<h2>개요</h2>
<p>이 페이지는 {service_name}의 버전별 상세 기능 내역을 관리합니다.</p>
<p>각 버전의 자세한 변경 사항, 새로운 기능, 버그 수정 내역 등이 포함됩니다.</p>

<h2>릴리즈 노트</h2>
<ac:structured-macro ac:name="children" ac:schema-version="2" ac:macro-id="release-notes-children" />
"""

    result = create_confluence_page(title, content, patch_notes_page_id, dry_run=False)

    if result.get("success"):
        page_id = result.get("id")
        print(f"\n✓ 상세 릴리즈 노트 페이지 생성 완료!")
        print(f"  페이지 ID: {page_id}")
        print(f"  URL: {result.get('url')}")
        return page_id
    else:
        print(f"\n✗ 페이지 생성 실패: {result.get('error')}")
        return None


def generate_patch_note_content(
    tag_info: Dict[str, str],
    commits: List[Dict[str, str]],
    tag_date: str,
    service_name: str,
    release_note_url: Optional[str] = None,
    is_new: bool = True,
) -> str:
    """간략한 패치노트 콘텐츠 생성"""
    env = tag_info["env"]
    version = tag_info["version"]
    env_kr = ENV_MAPPING.get(env, env)

    if is_new:
        # 새 문서: 배포 이력 + 주요 변경 사항
        html = f"""<h2>배포 이력</h2>
<table>
<tr><th>환경</th><th>배포 일시</th></tr>
<tr><td>{env_kr} ({env})</td><td>{tag_date}</td></tr>
</table>

<h2>주요 변경 사항</h2>
<p>총 {len(commits)}개의 커밋이 포함되어 있습니다.</p>
"""

        if commits:
            html += "<h3>주요 커밋</h3>\n<ul>\n"
            for commit in commits[:5]:
                html += f"<li><code>{commit['hash']}</code> - {commit['message']}</li>\n"
            if len(commits) > 5:
                html += f"<li>... 외 {len(commits) - 5}개 커밋</li>\n"
            html += "</ul>\n"

        if release_note_url:
            html += f"""<h2>상세 내역</h2>
<p>자세한 변경 사항은 <a href="{release_note_url}">상세 릴리즈 노트</a>를 참고하세요.</p>
"""
    else:
        # 기존 문서 업데이트: 반환 안함 (update_deployment_history 사용)
        html = ""

    return html


def generate_release_note_content(
    tag_info: Dict[str, str],
    commits: List[Dict[str, str]],
    file_changes: Dict[str, List[Dict[str, str]]],
    tag_date: str,
    service_name: str,
    is_new: bool = True,
) -> str:
    """상세 릴리즈 노트 콘텐츠 생성"""
    env = tag_info["env"]
    version = tag_info["version"]
    env_kr = ENV_MAPPING.get(env, env)

    if not is_new:
        # 기존 문서 업데이트: 배포 이력만 업데이트 (반환 안함)
        return ""

    # 배포 이력
    html = f"""<h2>배포 이력</h2>
<table>
<tr><th>환경</th><th>배포 일시</th></tr>
<tr><td>{env_kr} ({env})</td><td>{tag_date}</td></tr>
</table>

<h2>버전 정보</h2>
<table>
<tr><th>항목</th><th>내용</th></tr>
<tr><td>서비스</td><td>{service_name}</td></tr>
<tr><td>버전</td><td>{version}</td></tr>
</table>
"""

    # 변경 사항 - 커밋 히스토리
    html += "<h2>변경 사항</h2>\n<h3>Commit 히스토리</h3>\n"
    if commits:
        html += "<table>\n<tr><th>Hash</th><th>Author</th><th>Date</th><th>Message</th></tr>\n"
        for commit in commits:
            html += f"<tr><td><code>{commit['hash']}</code></td><td>{commit['author']}</td><td>{commit['date'][:10]}</td><td>{commit['message']}</td></tr>\n"
        html += "</table>\n"
    else:
        html += "<p>커밋 히스토리가 없습니다.</p>\n"

    # 변경된 파일 목록
    html += "<h3>변경된 파일</h3>\n"

    total_files = len(file_changes["added"]) + len(file_changes["modified"]) + len(file_changes["deleted"])
    html += f"<p>총 {total_files}개 파일 변경</p>\n"

    if file_changes["added"]:
        html += f"<h4>추가된 파일 ({len(file_changes['added'])}개)</h4>\n<ul>\n"
        for file in file_changes["added"][:20]:  # 최대 20개만 표시
            html += f"<li><code>{file['path']}</code> (+{file['added']} lines)</li>\n"
        if len(file_changes["added"]) > 20:
            html += f"<li>... 외 {len(file_changes['added']) - 20}개</li>\n"
        html += "</ul>\n"

    if file_changes["modified"]:
        html += f"<h4>수정된 파일 ({len(file_changes['modified'])}개)</h4>\n<ul>\n"
        for file in file_changes["modified"][:20]:
            if file.get("type") == "binary":
                html += f"<li><code>{file['path']}</code> (binary)</li>\n"
            else:
                html += f"<li><code>{file['path']}</code> (+{file['added']} -{file['deleted']} lines)</li>\n"
        if len(file_changes["modified"]) > 20:
            html += f"<li>... 외 {len(file_changes['modified']) - 20}개</li>\n"
        html += "</ul>\n"

    if file_changes["deleted"]:
        html += f"<h4>삭제된 파일 ({len(file_changes['deleted'])}개)</h4>\n<ul>\n"
        for file in file_changes["deleted"][:20]:
            html += f"<li><code>{file['path']}</code> (-{file['deleted']} lines)</li>\n"
        if len(file_changes["deleted"]) > 20:
            html += f"<li>... 외 {len(file_changes['deleted']) - 20}개</li>\n"
        html += "</ul>\n"

    # 배포 절차
    html += """<h2>배포 절차</h2>
<h3>배포 전 체크리스트</h3>
<ul>
<li>[ ] 코드 리뷰 완료</li>
<li>[ ] 테스트 통과 확인</li>
<li>[ ] 데이터베이스 마이그레이션 검토</li>
<li>[ ] 의존성 변경 사항 확인</li>
</ul>

<h3>배포 명령어</h3>
<pre><code>git checkout {env}-v{version}
# 배포 스크립트 실행
</code></pre>

<h3>배포 후 검증</h3>
<ul>
<li>[ ] 서비스 Health Check</li>
<li>[ ] API 응답 확인</li>
<li>[ ] 로그 확인</li>
<li>[ ] 모니터링 지표 확인</li>
</ul>
"""

    # 롤백 계획
    html += """<h2>롤백 계획</h2>
<h3>롤백 시나리오</h3>
<ul>
<li>서비스 장애 발생 시</li>
<li>심각한 버그 발견 시</li>
<li>성능 저하 발생 시</li>
</ul>

<h3>롤백 명령어</h3>
<pre><code># 이전 버전으로 롤백
# (이전 태그 확인 후 실행)
</code></pre>
"""

    return html


def create_confluence_page(title: str, content: str, parent_page_id: Optional[str] = None, dry_run: bool = False) -> Dict:
    """Confluence 페이지 생성"""
    if dry_run:
        print("=== DRY RUN MODE ===")
        print(f"Title: {title}")
        print(f"Parent Page ID: {parent_page_id}")
        print(f"Content:\n{content}")
        return {"success": True, "dry_run": True}

    # confluence.py 호출
    cmd = [
        "python3",
        CONFLUENCE_CLI,
        "create",
        "-s", "NAD",
        "-t", title,
        "-c", content,
    ]

    if parent_page_id:
        cmd.extend(["-p", parent_page_id])

    code, stdout, stderr = run_command(cmd)

    if code != 0:
        return {"error": f"Failed to create page: {stderr}"}

    try:
        result = json.loads(stdout)
        return result
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON response: {stdout}"}


def create_deployment_note(tag: str, prev_tag: Optional[str] = None, dry_run: bool = False, interactive: bool = True) -> Dict:
    """배포 노트 생성 메인 함수 (패치노트 + 상세 릴리즈 노트)"""
    # 태그 파싱
    tag_info = parse_tag(tag)
    if not tag_info:
        return {"error": f"Invalid tag format: {tag}. Expected format: {{env}}-v{{version}}"}

    # 레포지토리 확인
    repo_name = get_repo_name()
    if not repo_name or repo_name not in REPO_CONFIG:
        return {"error": f"Unsupported repository: {repo_name}"}

    config = REPO_CONFIG[repo_name]
    env = tag_info["env"]
    version = tag_info["version"]
    env_kr = ENV_MAPPING.get(env, env)

    # 이전 태그 자동 탐색 (같은 버전의 다른 환경 또는 이전 버전)
    if not prev_tag:
        prev_tag = get_prev_tag(tag, env)

    # Git 정보 수집
    commits = get_commits(prev_tag, tag)
    file_changes = get_file_changes(prev_tag, tag)
    tag_date = get_tag_date(tag)

    # 커밋 메시지에서 요약 생성
    summary = generate_summary_from_commits(commits)

    # 문서 제목 생성
    date_str = datetime.strptime(tag_date[:10], "%Y-%m-%d").strftime("%Y/%m/%d")
    patch_note_title = f"({date_str}) v{version} {summary}"
    release_note_title = f"v{version} 릴리즈 노트"

    # 1. 버전별 문서가 이미 있는지 확인
    existing_patch_id = search_version_document(version, config["patch_notes_page_id"], "patch")
    existing_release_id = None

    # 상세 릴리즈 노트 페이지 찾거나 생성
    release_notes_page_id = config.get("release_notes_page_id")
    if not release_notes_page_id:
        if interactive:
            print("\n=== 상세 릴리즈 노트 공간 설정 ===")
        release_notes_page_id = find_or_create_release_notes_page(
            config["patch_notes_page_id"],
            config["service_name"],
            interactive
        )
        if not release_notes_page_id:
            return {"error": "상세 릴리즈 노트 페이지를 찾거나 생성할 수 없습니다."}

    # 릴리즈 노트 문서 존재 여부 확인
    if release_notes_page_id:
        existing_release_id = search_version_document(version, release_notes_page_id, "release")

    # 2. 상세 릴리즈 노트 처리 (생성 또는 업데이트)
    release_note_url = None

    if existing_release_id:
        # 기존 릴리즈 노트가 있으면 배포 이력만 업데이트
        if interactive:
            print(f"\n=== 기존 릴리즈 노트 발견 (ID: {existing_release_id}) ===")
            print(f"배포 이력에 {env_kr} ({env}) 환경 추가")

        if not dry_run:
            update_result = update_deployment_history(
                existing_release_id,
                env,
                env_kr,
                tag_date
            )
            if "error" in update_result:
                return {"error": f"릴리즈 노트 업데이트 실패: {update_result.get('error')}"}

            # URL 가져오기
            page_info = get_confluence_page(existing_release_id)
            release_note_url = page_info.get("url")
    else:
        # 새 릴리즈 노트 생성
        release_note_content = generate_release_note_content(
            tag_info,
            commits,
            file_changes,
            tag_date,
            config["service_name"],
            is_new=True,
        )

        if dry_run or interactive:
            print(f"\n=== 상세 릴리즈 노트 미리보기 (신규 생성) ===")
            print(f"제목: {release_note_title}")
            print(f"부모 페이지 ID: {release_notes_page_id}")
            print(f"커밋 수: {len(commits)}, 파일 변경: {sum(len(v) for v in file_changes.values())}")
            if dry_run:
                print(f"\n내용:\n{release_note_content[:500]}...")

        if interactive and not dry_run:
            response = input("\n상세 릴리즈 노트를 생성하시겠습니까? (y/n): ")
            if response.lower() != 'y':
                return {"error": "사용자가 취소했습니다."}

        if not dry_run:
            release_result = create_confluence_page(
                release_note_title,
                release_note_content,
                release_notes_page_id,
                dry_run=False
            )

            if not release_result.get("success"):
                return {"error": f"상세 릴리즈 노트 생성 실패: {release_result.get('error')}"}

            release_note_url = release_result.get("url")

    # 3. 간략한 패치노트 처리 (생성 또는 업데이트)
    patch_note_url = None

    if existing_patch_id:
        # 기존 패치노트가 있으면 배포 이력만 업데이트
        if interactive:
            print(f"\n=== 기존 패치노트 발견 (ID: {existing_patch_id}) ===")
            print(f"배포 이력에 {env_kr} ({env}) 환경 추가")

        if not dry_run:
            update_result = update_deployment_history(
                existing_patch_id,
                env,
                env_kr,
                tag_date
            )
            if "error" in update_result:
                return {"error": f"패치노트 업데이트 실패: {update_result.get('error')}"}

            # URL 가져오기
            page_info = get_confluence_page(existing_patch_id)
            patch_note_url = page_info.get("url")
    else:
        # 새 패치노트 생성
        patch_note_content = generate_patch_note_content(
            tag_info,
            commits,
            tag_date,
            config["service_name"],
            release_note_url,
            is_new=True,
        )

        if dry_run or interactive:
            print(f"\n=== 패치노트 미리보기 (신규 생성) ===")
            print(f"제목: {patch_note_title}")
            print(f"부모 페이지 ID: {config['patch_notes_page_id']}")
            if dry_run:
                print(f"\n내용:\n{patch_note_content[:500]}...")

        if interactive and not dry_run:
            response = input("\n패치노트를 생성하시겠습니까? (y/n): ")
            if response.lower() != 'y':
                return {"error": "사용자가 취소했습니다."}

        if not dry_run:
            patch_result = create_confluence_page(
                patch_note_title,
                patch_note_content,
                config["patch_notes_page_id"],
                dry_run=False
            )

            if not patch_result.get("success"):
                return {"error": f"패치노트 생성 실패: {patch_result.get('error')}"}

            patch_note_url = patch_result.get("url")

    # 반환
    if not dry_run:
        return {
            "success": True,
            "tag": tag,
            "prev_tag": prev_tag,
            "commits": len(commits),
            "file_changes": sum(len(v) for v in file_changes.values()),
            "patch_note_url": patch_note_url,
            "release_note_url": release_note_url,
            "updated": bool(existing_patch_id or existing_release_id),
        }
    else:
        return {
            "success": True,
            "dry_run": True,
            "tag": tag,
            "prev_tag": prev_tag,
            "commits": len(commits),
            "file_changes": sum(len(v) for v in file_changes.values()),
            "existing_patch": bool(existing_patch_id),
            "existing_release": bool(existing_release_id),
        }


def main():
    parser = argparse.ArgumentParser(description="배포 노트 자동 생성")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create 명령
    create_parser = subparsers.add_parser("create", help="배포 노트 생성")
    create_parser.add_argument("--tag", help="배포 태그 (미지정 시 최신 태그 사용)")
    create_parser.add_argument("--prev-tag", help="이전 태그 (미지정 시 자동 탐색)")
    create_parser.add_argument("--dry-run", action="store_true", help="실제 생성하지 않고 미리보기")
    create_parser.add_argument("--no-interactive", action="store_true", help="대화형 모드 비활성화 (자동 생성)")

    args = parser.parse_args()

    if args.command == "create":
        # 태그 자동 탐색
        if not args.tag:
            code, stdout, _ = run_command(["git", "describe", "--tags", "--abbrev=0"])
            if code != 0:
                print(json.dumps({"error": "No tags found"}), file=sys.stderr)
                sys.exit(1)
            args.tag = stdout

        interactive = not args.no_interactive
        result = create_deployment_note(args.tag, args.prev_tag, args.dry_run, interactive)

        if not interactive or args.dry_run:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result.get("success"):
                if result.get("updated"):
                    print("\n✓ 배포 노트 업데이트 완료!")
                    print("  기존 문서에 배포 이력 추가됨")
                else:
                    print("\n✓ 배포 노트 생성 완료!")
                print(f"  패치노트: {result.get('patch_note_url')}")
                print(f"  상세 릴리즈 노트: {result.get('release_note_url')}")
            else:
                print(f"\n✗ 배포 노트 생성 실패: {result.get('error')}")

        if not result.get("success"):
            sys.exit(1)


if __name__ == "__main__":
    main()
