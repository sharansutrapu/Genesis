#!/bin/bash
# 🧬 Genesis Hive Mind — Environment Setup
# Run: chmod +x setup_hive.sh && ./setup_hive.sh

set -e

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║   🧬 Genesis Hive Mind — Setup                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# ── 1. Python Virtual Environment ─────────────────────────
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo "   ℹ️  Virtual environment already exists"
fi

source venv/bin/activate
echo "   ✅ Activated: $(python3 --version)"

# ── 2. Install Dependencies ───────────────────────────────
echo ""
echo "📦 Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "   ✅ Dependencies installed"

# ── 3. Verify Ollama ──────────────────────────────────────
echo ""
echo "🦙 Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "   ✅ Ollama found: $(ollama --version 2>/dev/null || echo 'version unknown')"
else
    echo "   ❌ Ollama not found!"
    echo "   Install from: https://ollama.com/"
    echo "   Then run: ollama serve"
    exit 1
fi

# ── 4. Pull Models ────────────────────────────────────────
echo ""
echo "📥 Pulling models (this may take a while on first run)..."

MODELS=("llama3.2" "deepseek-r1:1.5b" "qwen2.5:3b" "gemma2:2b" "phi3")

for model in "${MODELS[@]}"; do
    echo "   Pulling $model..."
    ollama pull "$model"
    echo "   ✅ $model ready"
done

# ── 5. Initialize Directories ─────────────────────────────
echo ""
echo "📂 Initializing directories..."
mkdir -p memory/chromadb_data
echo "   ✅ memory/chromadb_data/"

# ── 6. Run System Test ────────────────────────────────────
echo ""
echo "🔬 Running system test..."
python hive_orchestrator.py --test

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║   ✅ Setup Complete!                                  ║"
echo "║                                                       ║"
echo "║   Activate:  source venv/bin/activate                 ║"
echo "║   Run:       python hive_orchestrator.py -i           ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
