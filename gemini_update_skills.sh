#!/bin/bash

echo "🔄 최신 플러그인 업데이트를 위해 Git Pull을 수행합니다..."
# 스크립트가 위치한 디렉토리로 이동
cd "$(dirname "$0")" || exit
git pull

echo "📦 Gemini 스킬 최신화(재설치) 중..."
for d in plugins/*/; do
    gemini skills install "$d" --scope user
done

echo "✅ 스킬 업데이트 및 설치가 완료되었습니다!"
echo "💡 Gemini CLI가 실행 중이라면 프롬프트에 '/skills reload'를 입력하여 변경사항을 적용하세요."
