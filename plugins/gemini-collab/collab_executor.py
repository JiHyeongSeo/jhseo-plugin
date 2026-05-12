#!/usr/bin/env python3
import subprocess
import sys
import json
import argparse
from pathlib import Path

def collab_ask(message, tool="claude", work_dir=None):
    """Subprocess를 이용해 claude -p 를 실행하고 결과를 반환합니다."""
    if not work_dir:
        work_dir = str(Path.cwd())
    
    # Claude Code는 -p 또는 --print 옵션으로 비대화형 모드 실행 가능
    cmd = [tool, "-p", message]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=work_dir,
            timeout=180, # Claude는 좀 더 오래 걸릴 수 있으므로 3분
        )
        
        response = result.stdout.strip()
        # stderr에 에러가 있더라도 stdout에 결과가 있으면 결과로 간주 (warning 등 대응)
        if not response and result.returncode != 0:
            return {"error": f"{tool} 오류: {result.stderr.strip()[:500]}"}
        
        if not response:
            return {"error": f"{tool}에서 빈 응답이 반환되었습니다."}
            
        return {"response": response, "tool": tool}
        
    except FileNotFoundError:
        return {"error": f"{tool} CLI를 찾을 수 없습니다. 경로를 확인하세요."}
    except subprocess.TimeoutExpired:
        return {"error": f"{tool} 응답 타임아웃 (180초)"}
    except Exception as e:
        return {"error": f"실행 중 예외 발생: {str(e)}"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemini-Claude Collaboration Executor")
    # Gemini CLI가 스킬 도구를 호출할 때 --key value 형식으로 인자를 전달할 수 있으므로 대응
    parser.add_argument("positional_msg", nargs="?", help="메시지 (위치 인자)")
    parser.add_argument("--message", help="메시지 (이름 있는 인자)")
    parser.add_argument("--tool", default="claude", help="도구 이름 (기본: claude)")
    parser.add_argument("--work_dir", help="작업 디렉토리")
    
    args = parser.parse_args()
    
    # 위치 인자 또는 --message 인자 중 있는 것을 사용
    final_message = args.message if args.message else args.positional_msg
    
    if not final_message:
        print(json.dumps({"error": "메시지가 제공되지 않았습니다. --message 또는 첫 번째 인자로 메시지를 전달하세요."}))
        sys.exit(1)
        
    res = collab_ask(final_message, tool=args.tool, work_dir=args.work_dir)
    print(json.dumps(res, ensure_ascii=False))
