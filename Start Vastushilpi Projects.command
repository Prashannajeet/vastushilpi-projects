#!/bin/zsh
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv || exit 1
  .venv/bin/python -m pip install -r requirements.txt || exit 1
fi
if curl -fsS http://127.0.0.1:8501/_stcore/health >/dev/null 2>&1; then
  open http://127.0.0.1:8501
  exit 0
fi
(sleep 2; open http://127.0.0.1:8501) &
.venv/bin/python -m streamlit run streamlit_app.py --server.port 8501 --server.address 127.0.0.1
