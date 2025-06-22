# Sign-Stitch

Assembling videos of American Sign Language (ASL) signs by concatenating pre-recorded reference clips. Features:

- **Optional Stabilization**: Smooth out camera shake with FFmpeg’s `vidstabtransform`.
- **Speed Control**: Adjust playback speed (e.g. slow to 50% or speed up) via a simple flag.
- **Frame Rate Enforcement**: Output at any target FPS to match broadcast or platform requirements.
- **Flexible Invocation**: One-line Python script with intuitive flags; no manual FFmpeg editing.

---

## 📂 Project Layout

```
sign_stitch/
├── README.md
├── .gitignore
├── data/
│   └── ref_videos/              # Reference clips (A.mp4, B.mp4, etc.) + optional .trf
├── scripts/
│   ├── vidstab_detect.sh        # Motion-detect pass to create .trf files
│   ├── sign_stitch.py   # Main Python script (stabilize, speed, fps, stitch)
│   ├── concatenate_with_transitions.sh   # Bash equivalent
└── static/
    └── outputs/                 # Generated ASL videos
```

> **Note:** If you plan to use stabilization, run `vidstab_detect.sh` first to generate `<clip>.trf` files.

---

## 🛠 Prerequisites

1. **FFmpeg** with vidstab support:
   ```bash
   brew install ffmpeg
   brew install vidstab  # or compile with --enable-libvidstab
   ```

2. **Python 3.8+** (for the Python concat script):
   ```bash
   python3 -m venv asl-venv
   source asl-venv/bin/activate
   pip install moviepy imageio-ffmpeg
   ```

---

## 🚀 Quick Start

1. **Motion Detection (vidstabdetect)**  
   Generate stabilization data for each clip. This is a **two-pass** process:

   - **Pass 1 – Detection:**  Examine each frame (or every Nth if you customize) to estimate camera motion.
     ```bash
     ffmpeg -i data/ref_videos/*.mp4 \
       -vf vidstabdetect=shakiness=5:accuracy=15:result=data/ref_videos/<clip>.trf \
       -f null -
     ```
     - `shakiness` (0–10): Sensitivity to small vibrations (higher = more sensitive).
     - `accuracy` (1–15): Finer motion grid (higher = slower but more precise).

   - **Pass 2 – Transformation:**  Apply the transforms to each clip to stabilize.
     ```bash
     ffmpeg -i data/ref_videos/<clip>.mp4 \
       -vf vidstabtransform=input=data/ref_videos/<clip>.trf:smoothing=30:zoom=2:interpol=linear \
       -c:v libx264 -an static/outputs/<clip>_stab.mp4
     ```
     - `smoothing` (0–200+): Number of frames to average for a smooth result.
     - `zoom`/`optzoom` (0–2): Slight zoom to hide black borders from shifting.
     - `interpol` (`linear`/`bicubic`): Interpolation method for sub-pixel accuracy.

   > **Tip:** Tweak `shakiness`, `accuracy`, and `smoothing` in `scripts/vidstab_detect.sh` and in the Python script’s `--no-stab` section to find the right balance for your footage.

2. **Stitch Clips (sign_stitch.py)**
   ```bash
   # Default: stabilize + 50% speed + 60 FPS
   python scripts/sign_stitch.py A B C
   ```
   Flags:

   | Flag            | Description                                                      | Default |
   |-----------------|------------------------------------------------------------------|---------|
   | `--no-stab`     | Skip stabilization; faster but raw camera shake remains.         | False   |
   | `--speed <val>` | Playback speed multiplier (e.g. `2.0` → half-speed).             | 2.0     |
   | `--fps <val>`   | Target output frame rate (e.g. `60`, `30`, `24`).                | 60      |

3. **Result**
   The final video `<letters>.mp4` (e.g. `ABC.mp4`) is saved in `static/outputs/`.

---

## ⚙ .gitignore

```gitignore
# Python env
easl-venv/

# Reference & temp files
data/ref_videos/*.trf
data/ref_videos/*.mp4  # optional
temp_clips/
static/outputs/