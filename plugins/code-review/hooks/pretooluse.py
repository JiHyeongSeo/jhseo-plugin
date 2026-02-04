#!/usr/bin/env python3
"""PreToolUse hook for code-review plugin.

Detects git commit commands and triggers AI code review.
"""

import sys
import json
import subprocess
from pathlib import Path

# Language mapping by file extension
LANG_MAP = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript (React)',
    '.jsx': 'JavaScript (React)',
    '.java': 'Java',
    '.go': 'Go',
    '.rs': 'Rust',
    '.sql': 'SQL',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.cs': 'C#',
    '.cpp': 'C++',
    '.c': 'C',
    '.kt': 'Kotlin',
    '.swift': 'Swift',
    '.scala': 'Scala',
}


def is_git_commit_command(tool_name: str, tool_input: dict) -> bool:
    """Check if the tool call is a git commit command."""
    if tool_name != 'Bash':
        return False

    command = tool_input.get('command', '')

    # Check for git commit patterns
    commit_patterns = [
        'git commit',
        'git commit -m',
        'git commit -am',
        'git commit --amend',
    ]

    return any(pattern in command for pattern in commit_patterns)


def get_staged_diff() -> str:
    """Get staged diff content."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--staged'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout
    except Exception as e:
        return f"Error getting diff: {e}"


def get_staged_files() -> list[str]:
    """Get list of staged file names."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--staged', '--name-only'],
            capture_output=True,
            text=True,
            timeout=10
        )
        files = result.stdout.strip().split('\n')
        return [f for f in files if f]
    except Exception:
        return []


def get_file_content(filepath: str) -> str:
    """Get staged file content using git show."""
    try:
        result = subprocess.run(
            ['git', 'show', f':{filepath}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout
    except Exception as e:
        return f"Error reading file: {e}"


def detect_language(filepath: str) -> str:
    """Detect programming language from file extension."""
    ext = Path(filepath).suffix.lower()
    return LANG_MAP.get(ext, 'Unknown')


def get_gitignore_content() -> str:
    """Read .gitignore file content."""
    try:
        gitignore_path = Path('.gitignore')
        if gitignore_path.exists():
            return gitignore_path.read_text()
        return "(No .gitignore file found)"
    except Exception as e:
        return f"Error reading .gitignore: {e}"


def build_review_prompt(files: list[str], diff: str, file_contents: dict[str, str], gitignore: str) -> str:
    """Build the code review prompt."""

    # Detect languages
    languages = list(set(detect_language(f) for f in files))
    languages_str = ', '.join(languages)

    # Build file contents section
    full_code_sections = []
    for filepath, content in file_contents.items():
        lang = detect_language(filepath)
        full_code_sections.append(f"### {filepath} ({lang})\n```\n{content}\n```")

    full_code = '\n\n'.join(full_code_sections)
    file_list = '\n'.join(f'- {f}' for f in files)

    prompt = f"""# 코드리뷰 수행

당신은 20년 경력의 시니어 개발자입니다. 실무 경험을 바탕으로 실용적인 코드리뷰를 수행합니다.

## 리뷰 대상
- 언어: {languages_str}
- 파일:
{file_list}

## 변경 내용 (Diff)
```diff
{diff}
```

## 변경 후 전체 코드
{full_code}

## .gitignore 현황
```
{gitignore}
```

## 리뷰 기준

### 카테고리별 체크
1. **Type Safety**: 타입 안정성, any 남용, 타입 추론 이슈
2. **Readability**: 가독성, 네이밍, 코드 구조
3. **Security**: 민감정보 노출, SQL injection, XSS 등
4. **Performance**: 시간복잡도 O(n²) 이상, 불필요한 연산, 메모리 낭비
5. **Database**: N+1 쿼리, 인덱스 미사용, 트랜잭션 이슈
6. **Architecture**: DTO 구조, 중복 코드 (3회 이상), 책임 분리
7. **Gitignore**: 민감 파일(.env, credentials, *.key 등)이 .gitignore에 포함되어 있는지

### 심각도 분류
- **Critical**: 즉시 수정 (보안, 심각한 버그)
- **Major**: 수정 권장 (성능, 타입 이슈)
- **Minor**: 개선 제안 (가독성, 리팩토링)

### 필수 vs 선택 구분 (시니어 관점)
각 이슈에 대해 실무 경험을 바탕으로 판단:
- **🔴 필수 (MUST FIX)**: 프로덕션 배포 전 반드시 수정. 안 하면 장애/보안사고 발생
- **🟡 권장 (SHOULD FIX)**: 코드 품질 향상. 기술 부채 누적 방지
- **🔵 선택 (NICE TO HAVE)**: 시간 여유 있을 때. 완벽주의적 개선

## 출력 형식

### 요약
- 전체 이슈 수: N개
- 필수: N개 / 권장: N개 / 선택: N개
- 총평: (한 줄 요약)

### 이슈 목록
각 이슈에 대해:

## [심각도] 카테고리 - [필수/권장/선택]

**파일:** 파일명
**라인:** 라인번호

**문제점:**
왜 문제인지, 어떤 상황에서 문제가 되는지 설명

**Before:**
```언어
문제 코드
```

**After:**
```언어
개선된 코드
```

**우선순위:** 1-5

---

### 리팩토링 제안 (있다면)
- 현재 구조의 문제점
- 제안하는 구조
- 예상 효과

### 시니어 한마디
실무 관점에서 이 코드에 대한 총평과 조언

---

이슈가 없다면 "이슈 없음 - 코드가 잘 작성되었습니다." 라고 말해주세요.
Critical 이슈가 있다면 반드시 먼저 언급하고, commit을 진행하기 전 수정을 강력히 권고해주세요.
"""

    return prompt


def main():
    """Main entry point for PreToolUse hook."""
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})

        # Check if this is a git commit command
        if not is_git_commit_command(tool_name, tool_input):
            # Not a git commit, pass through
            print(json.dumps({}), file=sys.stdout)
            sys.exit(0)

        # Get staged changes
        staged_files = get_staged_files()

        if not staged_files:
            print(json.dumps({
                "systemMessage": "No staged files to review"
            }), file=sys.stdout)
            sys.exit(0)

        # Get diff and file contents
        diff = get_staged_diff()
        file_contents = {}

        for filepath in staged_files:
            content = get_file_content(filepath)
            if content and not content.startswith("Error"):
                file_contents[filepath] = content

        # Get gitignore content
        gitignore = get_gitignore_content()

        # Build review prompt
        review_prompt = build_review_prompt(
            staged_files, diff, file_contents, gitignore
        )

        # Output systemMessage with review prompt
        result = {
            "systemMessage": review_prompt
        }

        print(json.dumps(result), file=sys.stdout)

    except Exception as e:
        # On any error, allow the operation and log
        error_output = {
            "systemMessage": f"Code review hook error: {str(e)}"
        }
        print(json.dumps(error_output), file=sys.stdout)

    finally:
        # Always exit 0 - never block operations due to hook errors
        sys.exit(0)


if __name__ == '__main__':
    main()
