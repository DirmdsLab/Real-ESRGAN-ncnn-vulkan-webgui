#!/usr/bin/env bash
set -e

echo "[INFO] Installing system packages..."

apt update
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    libgomp1 \
    vulkan-tools

echo "[INFO] Creating virtual environment..."

python3 -m venv /opt/venv

. /opt/venv/bin/activate

pip install --upgrade pip --disable-pip-version-check
pip install -r /upscale/requirements.txt --disable-pip-version-check

touch /opt/venv/.setup_done

echo "[INFO] Setup completed"