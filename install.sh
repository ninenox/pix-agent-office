#!/usr/bin/env bash
# Claude Agent Office — Installer
set -e

# ─── Colors ───
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

ok()   { echo -e "${GREEN}  ✓${NC} $1"; }
info() { echo -e "${CYAN}  →${NC} $1"; }
warn() { echo -e "${YELLOW}  ⚠${NC} $1"; }
err()  { echo -e "${RED}  ✗${NC} $1"; exit 1; }

echo -e "\n${BOLD}🏢 Claude Agent Office — Setup${NC}\n"

# ─── Check OS ───
case "$(uname -s)" in
  Darwin*) OS="macOS" ;;
  Linux*)  OS="Linux" ;;
  *)       err "รองรับเฉพาะ macOS และ Linux" ;;
esac
ok "OS: $OS"

# ─── Check Python ───
if command -v python3 &>/dev/null; then
  PY="python3"
elif command -v python &>/dev/null; then
  PY="python"
else
  err "ไม่พบ Python — ติดตั้งได้ที่ https://python.org"
fi

PY_VERSION=$($PY -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$($PY -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$($PY -c 'import sys; print(sys.version_info.minor)')

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
  err "ต้องใช้ Python 3.10+ (พบ $PY_VERSION)"
fi
ok "Python $PY_VERSION"

# ─── Check uv or pip ───
USE_UV=false
if command -v uv &>/dev/null; then
  USE_UV=true
  ok "uv $(uv --version | awk '{print $2}')"
else
  warn "ไม่พบ uv — จะใช้ pip แทน"
  info "ติดตั้ง uv เพื่อความเร็วกว่า: pip install uv"
fi

# ─── Create .venv ───
VENV_DIR=".venv"

if [ -d "$VENV_DIR" ]; then
  warn "พบ $VENV_DIR อยู่แล้ว — ข้ามขั้นตอนสร้าง venv"
else
  info "สร้าง virtual environment..."
  if $USE_UV; then
    uv venv "$VENV_DIR" --python "$PY_VERSION" --quiet
  else
    $PY -m venv "$VENV_DIR"
  fi
  ok "สร้าง $VENV_DIR เรียบร้อย"
fi

# ─── Activate venv ───
if [ -f "$VENV_DIR/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"
  ok "Activated: $VENV_DIR"
else
  err "ไม่พบ $VENV_DIR/bin/activate"
fi

# ─── Install dependencies ───
info "ติดตั้ง dependencies จาก backend/requirements.txt..."

if $USE_UV; then
  uv pip install -r backend/requirements.txt --quiet
else
  pip install -r backend/requirements.txt --quiet
fi
ok "ติดตั้ง dependencies เสร็จแล้ว"

# ─── Init state.json ───
if [ ! -f "state.json" ]; then
  cp state.sample.json state.json
  ok "สร้าง state.json จาก template"
else
  warn "state.json มีอยู่แล้ว — ข้าม"
fi

# ─── Check API key ───
echo ""
if [ -z "$ANTHROPIC_API_KEY" ]; then
  warn "ยังไม่มี ANTHROPIC_API_KEY — รันได้แค่ demo mode"
  echo -e "      ตั้งค่าด้วย: ${CYAN}export ANTHROPIC_API_KEY=sk-ant-...${NC}"
else
  ok "ANTHROPIC_API_KEY พบแล้ว"
fi

# ─── Done ───
echo ""
echo -e "${BOLD}${GREEN}✅ ติดตั้งสำเร็จ!${NC}"
echo ""
echo -e "${BOLD}วิธีใช้งาน:${NC}"
echo ""
echo -e "  ${CYAN}source .venv/bin/activate${NC}          # activate venv"
echo ""
echo -e "  ${CYAN}python main.py --server-only${NC}       # Demo mode (ไม่ต้องมี API key)"
echo -e "                                      → http://localhost:19000"
echo ""
echo -e "  ${CYAN}python main.py${NC}                     # Full mode (ต้องมี API key)"
echo ""
echo -e "  ${CYAN}python main.py --tasks tasks.json${NC}  # Custom tasks"
echo ""
echo -e "  ${CYAN}python set_state.py claude-opus writing \"กำลังทำงาน\"${NC}"
echo ""
