#!/usr/bin/env bash
set -e

if [ ! -f /opt/venv/.setup_done ]; then
    /upscale/setup.sh
fi

. /opt/venv/bin/activate

echo "===== Vulkan GPU Check ====="

vulkaninfo 2>/dev/null | grep deviceName || true

echo "============================"

cd /upscale

chmod +x run.sh

exec ./run.sh