#!/bin/bash
source /opt/mineru_venv/bin/activate
/monitor_script.sh
exec "$@"