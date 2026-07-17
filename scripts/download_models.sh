#!/usr/bin/env bash
# Downloads the dlib 68-point facial landmark predictor into models/.
# (The Haar cascade face detector no longer needs downloading — the app
# uses the copy bundled with opencv-python via cv2.data.haarcascades.)
set -e

MODELS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/models"
mkdir -p "$MODELS_DIR"

URL="http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
DEST_BZ2="$MODELS_DIR/shape_predictor_68_face_landmarks.dat.bz2"
DEST="$MODELS_DIR/shape_predictor_68_face_landmarks.dat"

if [ -f "$DEST" ]; then
  echo "Already present: $DEST"
  exit 0
fi

echo "Downloading facial landmark model (~99 MB) from dlib.net..."
curl -L -o "$DEST_BZ2" "$URL"

echo "Extracting..."
bzip2 -d "$DEST_BZ2"

echo "Done -> $DEST"
