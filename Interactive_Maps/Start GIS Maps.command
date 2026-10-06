#!/bin/zsh
cd "$(dirname "$0")"
export PROJ_LIB='/Applications/QGIS-LTR.app/Contents/Resources/proj'
if curl -fsS http://127.0.0.1:8765/assets/config.json >/dev/null 2>&1; then
 open http://127.0.0.1:8765/grid
 exit 0
fi
(sleep 2; open http://127.0.0.1:8765/grid) &
'/Applications/QGIS-LTR.app/Contents/MacOS/bin/python3' server.py --port 8765
