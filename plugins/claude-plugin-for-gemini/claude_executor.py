#!/usr/bin/env python3
import subprocess
import sys
import json
import argparse
import os
from pathlib import Path

def get_git_context():
    """Git 관련 컨텍스트(상태, 변경사항 요약)를 가져옵니다."""
    try:
        status = subprocess.check_output(["git", "status", "--short"], text=True, stderr=subprocess.DEVNULL)
        diff = subprocess.check_output(["git", "diff", "--stat"], text=True, stderr=subprocess.DEVNULL)
        return f"\n\n[Git Status]\n{status}\n[Git Diff Summary]\n{diff}"
    except:
        return ""

def get_file_list():
    """현재 디렉토리의 주요 파일 목록을 가져옵니다."""
    try:
        files = subprocess.check_output(["find", ".", "-maxdepth", "2", "-not", "-path", '*/.*'], text=True, stderr=subprocess.DEVNULL)
        return f"\n\n[File Structure]\n{files}"
    except:
        return ""

def claude_ask(message, include_context=True, tool="claude", work_dir=None):
    """Claude Code CLI를 호출하여 협업을 수행합니다."""
    if not work_dir:
        work_dir = str(Path.cwd())
    
    full_prompt = message
    if include_context:
        context = ""
        context += get_git_context()
        context += get_file_list()
        if context:
            full_prompt = f"{message}\n\n--- Context for collaboration ---\n{context}\n--- End of Context ---"

    # Claude Code는 -p 또는 --print 옵션으로 비대화형 모드 실행 가능
    cmd = [tool, "-p", full_prompt]
    
    try:
        # 환경 변수 유지 (API Key 등 필요할 수 있음)
        env = os.environ.copy()
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=work_dir,
            env=env,
            timeout=300, # 복잡한 작업은 5분까지 허용
        )
        
        response = result.stdout.strip()
        
        if not response and result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "알 수 없는 오류"
            return {"error": f"{tool} 실행 오류 (코드 {result.returncode}): {error_msg[:500]}"}
        
        if not response:
            return {"error": f"{tool}에서 응답을 생성하지 못했습니다."}
            
        return {
            "response": response,
            "tool": tool,
            "context_included": include_context
        }
        
    except FileNotFoundError:
        return {"error": f"'{tool}' 명령어를 찾을 수 없습니다. Claude Code가 설치되어 있는지 확인하세요."}
    except subprocess.TimeoutExpired:
        return {"error": f"Claude 응답 타임아웃 (300초)"}
    except Exception as e:
        return {"error": f"실행 중 예외 발생: {str(e)}"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Claude Plugin for Gemini Executor")
    parser.add_argument("positional_msg", nargs="?", help="메시지 (위치 인자)")
    parser.add_argument("--message", help="메시지 (이름 있는 인자)")
    parser.add_argument("--include_context", type=str, default="true", help="컨텍스트 포함 여부 (true/false)")
    parser.add_argument("--tool", default="claude", help="도구 이름 (기본: claude)")
    parser.add_argument("--work_dir", help="작업 디렉토리")
    
    args = parser.parse_args()
    
    final_message = args.message if args.message else args.positional_msg
    include_ctx = args.include_context.lower() == "true"
    
    if not final_message:
        print(json.dumps({"error": "메시지가 제공되지 않았습니다."}))
        sys.exit(1)
        
    res = claude_ask(final_message, include_context=include_ctx, tool=args.tool, work_dir=args.work_dir)
    print(json.dumps(res, ensure_ascii=False))
