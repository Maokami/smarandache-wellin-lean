#!/usr/bin/env bash
# 블루프린트 빌드와 검사.
#   scripts/blueprint.sh            웹 판 + PDF 판 + 빠른 대응 검사
#   scripts/blueprint.sh --lean     위에 더해 Lean 이름 존재 검사 (lake env lean, 수 분)
#   scripts/blueprint.sh serve      로컬 웹 서버 (http://127.0.0.1:8000)
# 필요: leanblueprint (uv tool install leanblueprint), graphviz, XeLaTeX (TeX Live)
set -euo pipefail
cd "$(dirname "$0")/.."
TOOLBIN="$HOME/.local/share/uv/tools/leanblueprint/bin"   # plastex 이 여기 있다
for d in "$TOOLBIN" /usr/local/texlive/2026/bin/universal-darwin; do
  [ -d "$d" ] && PATH="$d:$PATH"
done
export PATH
if [ "${1:-}" = "serve" ]; then
  exec python3 -m http.server 8000 --bind 127.0.0.1 --directory blueprint/web
fi
leanblueprint web
leanblueprint pdf
python3 -I scripts/check_blueprint.py ${1:+"$1"}
