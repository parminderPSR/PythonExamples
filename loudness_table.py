import subprocess
import re
import sys
import os

def extract_loudness_info(ffmpeg_output):
    patterns = {
        "I": r"I:\s*(-?\d+\.\d+) LUFS",
        "Threshold (I)": r"Integrated loudness:\s*\n\s*I:.*\n\s*Threshold:\s*(-?\d+\.\d+) LUFS",
        "LRA": r"LRA:\s*(-?\d+\.\d+) LU",
        "Threshold (LRA)": r"Loudness range:\s*\n\s*LRA:.*\n\s*Threshold:\s*(-?\d+\.\d+) LUFS",
        "LRA low": r"LRA low:\s*(-?\d+\.\d+) LUFS",
        "LRA high": r"LRA high:\s*(-?\d+\.\d+) LUFS"
    }
    matches = {}
    for key, pattern in patterns.items():
        m = re.search(pattern, ffmpeg_output, re.MULTILINE)
        matches[key] = m.group(1) if m else "N/A"
    return matches

def process_file(filepath):
    cmd = [
        "ffmpeg", "-i", filepath,
        "-filter:a", "ebur128=framelog=quiet",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    output = result.stderr
    info = extract_loudness_info(output)
    return [os.path.basename(filepath), info['I'], info['Threshold (I)'], info['LRA'], info['Threshold (LRA)'], info['LRA low'], info['LRA high']]

def main(target):

    files = []
    if os.path.isfile(target) and target.endswith('.m4a'):
        files = [target]
    elif os.path.isdir(target):
        files = [os.path.join(target, f) for f in os.listdir(target) if f.endswith('.m4a')]
        files.sort()  # Sort files alphabetically
    else:
        print("Input must be a .m4a file or a folder containing .m4a files.")
        sys.exit(1)

    rows = []
    for f in files:
        print(f"Processing: {f}")
        rows.append(process_file(f))

    md_file = "loudness_report.md"
    with open(md_file, "w") as f:
        f.write("| Song Name | I (LUFS) | Threshold (I) | LRA (LU) | Threshold (LRA) | LRA low | LRA high |\n")
        f.write("|-----------|----------|---------------|----------|-----------------|---------|----------|\n")
        for row in rows:
            f.write("| " + " | ".join(row) + " |\n")
    print(f"Markdown report generated: {md_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 loudness_table.py <file.m4a|folder>")
        sys.exit(1)
    main(sys.argv[1])
