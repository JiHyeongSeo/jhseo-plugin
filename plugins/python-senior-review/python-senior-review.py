#!/usr/bin/env python3
"""Python Senior Review CLI - pyright 정적 분석 + 시니어 리뷰용 스크립트"""

import argparse
import json
import subprocess
from pathlib import Path


def run_pyright(target: str) -> dict:
    """pyright를 실행하고 결과를 반환"""
    try:
        result = subprocess.run(
            ["pyright", "--outputjson", target],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.stdout:
            data = json.loads(result.stdout)
            return {
                "success": True,
                "summary": data.get("summary", {}),
                "diagnostics": data.get("generalDiagnostics", []),
                "version": data.get("version", "unknown")
            }
        else:
            return {
                "success": False,
                "error": result.stderr or "No output from pyright"
            }

    except FileNotFoundError:
        return {
            "success": False,
            "error": "pyright not found. Install with: pip install pyright"
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "pyright timed out after 60 seconds"
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse pyright output: {e}"
        }


def format_diagnostics(diagnostics: list) -> str:
    """진단 결과를 읽기 쉬운 형식으로 변환"""
    if not diagnostics:
        return "No issues found."

    lines = []
    severity_emoji = {
        "error": "🔴",
        "warning": "🟡",
        "information": "🔵"
    }

    for diag in diagnostics:
        sev = diag.get("severity", "information")
        emoji = severity_emoji.get(sev, "⚪")
        file_path = diag.get("file", "unknown")

        range_info = diag.get("range", {})
        start = range_info.get("start", {})
        line = start.get("line", 0) + 1  # 0-indexed to 1-indexed

        message = diag.get("message", "No message")
        rule = diag.get("rule", "")

        location = f"{Path(file_path).name}:{line}"
        rule_str = f" [{rule}]" if rule else ""

        lines.append(f"{emoji} {location}{rule_str}: {message}")

    return "\n".join(lines)


def analyze(target: str, output_format: str = "json") -> None:
    """파일 또는 디렉토리를 분석"""
    result = run_pyright(target)

    if output_format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # human-readable format
        if not result["success"]:
            print(f"Error: {result['error']}")
            return

        summary = result.get("summary", {})
        print("=" * 50)
        print("PYRIGHT ANALYSIS RESULT")
        print("=" * 50)
        print(f"Files analyzed: {summary.get('filesAnalyzed', 0)}")
        print(f"Errors: {summary.get('errorCount', 0)}")
        print(f"Warnings: {summary.get('warningCount', 0)}")
        print(f"Information: {summary.get('informationCount', 0)}")
        print()
        print("DIAGNOSTICS:")
        print("-" * 50)
        print(format_diagnostics(result.get("diagnostics", [])))


def check_pyright() -> None:
    """pyright 설치 여부 확인"""
    try:
        result = subprocess.run(
            ["pyright", "--version"],
            capture_output=True,
            text=True
        )
        print(json.dumps({
            "installed": True,
            "version": result.stdout.strip()
        }))
    except FileNotFoundError:
        print(json.dumps({
            "installed": False,
            "install_command": "pip install pyright"
        }))


def main():
    parser = argparse.ArgumentParser(
        description="Python Senior Review - pyright 기반 정적 분석"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="파일 또는 디렉토리를 pyright로 분석"
    )
    analyze_parser.add_argument(
        "target",
        help="분석할 파일 또는 디렉토리 경로"
    )
    analyze_parser.add_argument(
        "-f", "--format",
        choices=["json", "text"],
        default="json",
        help="출력 형식 (기본: json)"
    )

    # check command
    subparsers.add_parser(
        "check",
        help="pyright 설치 여부 확인"
    )

    args = parser.parse_args()

    if args.command == "analyze":
        analyze(args.target, args.format)
    elif args.command == "check":
        check_pyright()


if __name__ == "__main__":
    main()
