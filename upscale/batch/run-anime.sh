#!/usr/bin/env bash

set -euo pipefail

# Change to the directory where this script is located
cd "$(dirname "$(realpath "$0")")"

# Real-ESRGAN binary
binrealesrgan="../realesrgan-ncnn-vulkan-20220424-ubuntu/realesrgan-ncnn-vulkan"

input_dir="input"
output_dir="output"

# Counters
total_files=0
processed_files=0
skipped_files=0
failed_files=0

# Check Real-ESRGAN binary
if [[ ! -x "$binrealesrgan" ]]; then
    echo "Error: Real-ESRGAN binary not found or not executable:"
    echo "  $binrealesrgan"
    exit 1
fi

# Count all image files first
total_files=$(
    find "$input_dir" -type f \
        \( \
            -iname '*.png' \
            -o -iname '*.jpg' \
            -o -iname '*.jpeg' \
            -o -iname '*.webp' \
            -o -iname '*.bmp' \
            -o -iname '*.tif' \
            -o -iname '*.tiff' \
            -o -iname '*.gif' \
        \) \
        -print | wc -l
)

echo "========================================"
echo "Real-ESRGAN Anime Upscaler"
echo "========================================"
echo "Total image files found: $total_files"
echo

# Scan all image files
while IFS= read -r -d '' input_file; do

    filename="$(basename "$input_file")"
    name="${filename%.*}"
    extension="${filename##*.}"

    # Skip files that have already been processed
    if [[ "$name" == *_done ]]; then
        skipped_files=$((skipped_files + 1))

        echo "Skip: $input_file"
        echo "Progress: $processed_files/$total_files converted"
        echo

        continue
    fi

    output_file="$output_dir/${name}_upscale.png"
    done_file="$input_dir/${name}_done.${extension}"

    echo "========================================"
    echo "Processing [$((processed_files + 1))/$total_files]"
    echo "Input : $input_file"
    echo "Output: $output_file"
    echo "========================================"

    # Run Real-ESRGAN
    if "$binrealesrgan" \
        -i "$input_file" \
        -s 4 \
        -n realesrgan-x4plus-anime \
        -o "$output_file" \
        -f png
    then
        # Rename the input only after successful upscaling
        mv -- "$input_file" "$done_file"

        processed_files=$((processed_files + 1))

        echo
        echo "Done: $done_file"
        echo "Progress: $processed_files/$total_files converted"
    else
        failed_files=$((failed_files + 1))

        echo
        echo "Error: Upscaling failed:"
        echo "  $input_file"
        echo "  Input file was not renamed."
        echo "Failed: $failed_files"
    fi

    echo

done < <(
    find "$input_dir" -type f \
        \( \
            -iname '*.png' \
            -o -iname '*.jpg' \
            -o -iname '*.jpeg' \
            -o -iname '*.webp' \
            -o -iname '*.bmp' \
            -o -iname '*.tif' \
            -o -iname '*.tiff' \
            -o -iname '*.gif' \
        \) \
        -print0
)

echo "========================================"
echo "Processing Summary"
echo "========================================"
echo "Total files found : $total_files"
echo "Converted         : $processed_files"
echo "Skipped (_done)   : $skipped_files"
echo "Failed            : $failed_files"
echo "========================================"