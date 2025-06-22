#!/usr/bin/env python3
"""
scripts/concatenate_with_transitions.py

Stabilize (optional), adjust speed factor, and concatenate ASL reference clips uniformly at specified FPS.

Usage:
    python scripts/concatenate_with_transitions.py [--no-stab] [--speed FACTOR] [--fps FPS] A B C ...

Flags:
    --no-stab       Disable stabilization step (skip vidstabtransform)
    --speed FACTOR  Playback speed multiplier (e.g., 2.0 for half-speed) [default: 2.0]
    --fps FPS       Output frame rate [default: 60]
"""
import sys
import os
import subprocess
import shutil
import tempfile
import argparse

# Base directories
REF_DIR = "data/ref_videos"
OUT_DIR = "static/outputs"


def run(cmd):
    """Run a shell command, printing it first."""
    print("⏳", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main(args):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp_dir = tempfile.mkdtemp(prefix="asl_tmp_")
    processed = []

    for letter in args.letters:
        src = os.path.join(REF_DIR, f"{letter.upper()}.mp4")
        if not os.path.isfile(src):
            shutil.rmtree(tmp_dir)
            raise FileNotFoundError(f"Missing reference video: {src}")

        filters = []
        if args.stab:
            trf = src.replace('.mp4', '.trf')
            if not os.path.isfile(trf):
                shutil.rmtree(tmp_dir)
                raise FileNotFoundError(
                    f"Missing transform file: {trf}. Run vidstab_detect.sh first."
                )
            filters.append(
                f"vidstabtransform=input='{trf}':smoothing=30:interpol=linear"
            )
        # apply speed-adjustment
        filters.append(f"setpts={args.speed}*PTS")
        # enforce FPS
        filters.append(f"fps={args.fps}")

        vf = ",".join(filters)
        dst = os.path.join(tmp_dir, f"{letter}_proc.mp4")

        run([
            'ffmpeg', '-y', '-i', src,
            '-vf', vf,
            '-c:v', 'libx264', '-r', str(args.fps), '-an', dst
        ])
        processed.append(dst)

    # write concat list
    list_file = os.path.join(tmp_dir, 'concat_list.txt')
    with open(list_file, 'w') as f:
        for p in processed:
            f.write(f"file '{p}'\n")

    # concatenate without re-encoding
    # output filename: just the joined letters
    out_name = f"{''.join(args.letters)}.mp4"
    out_path = os.path.join(OUT_DIR, out_name)
    run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', list_file,
        '-c', 'copy', out_path
    ])

    shutil.rmtree(tmp_dir)
    print(f"✅ Created {out_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Concatenate ASL reference clips with optional stabilization and speed control"
    )
    parser.add_argument(
        '--no-stab', dest='stab', action='store_false',
        help='disable stabilization step'
    )
    parser.set_defaults(stab=True)
    parser.add_argument(
        '--speed', type=float, default=2.0,
        help='playback speed factor (e.g. 2.0 for half-speed)'
    )
    parser.add_argument(
        '--fps', type=int, default=60,
        help='output frame rate'
    )
    parser.add_argument(
        'letters', nargs='+',
        help='Sequence of clip names (without .mp4) to concatenate'
    )
    args = parser.parse_args()
    main(args)
