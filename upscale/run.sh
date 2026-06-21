#!/usr/bin/env bash

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$ROOT_DIR"

mkdir -p pyserver/input
mkdir -p pyserver/output

chmod +x \
    realesrgan-ncnn-vulkan-20220424-ubuntu/realesrgan-ncnn-vulkan

echo "[INFO] Installing Python dependencies..."
pip3 install -r requirements.txt

echo "[INFO] Starting Real-ESRGAN WebGUI"

exec python3 pyserver/app.py