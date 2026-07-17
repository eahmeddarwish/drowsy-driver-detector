#!/usr/bin/env bash
# Raspberry Pi OS / Debian / Ubuntu system packages needed before `pip
# install -r requirements.txt` will succeed (dlib compiles from source,
# and espeak is the text-to-speech engine used for spoken alerts).
set -e

sudo apt-get update
sudo apt-get install -y \
  build-essential cmake \
  libopenblas-dev liblapack-dev \
  libx11-dev libgtk-3-dev \
  python3-dev python3-pip \
  espeak

echo "System dependencies installed. Now run:"
echo "  pip install -r requirements.txt"
echo "  bash scripts/download_models.sh"
