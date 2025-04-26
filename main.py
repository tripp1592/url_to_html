#!/usr/bin/env python3
import configparser
import subprocess
import sys
import shutil
import os
from urllib.parse import urlparse, quote


def load_config(path="config.ini"):
    cfg = configparser.ConfigParser()
    cfg.read(path)
    m = cfg["mirror"]
    return {
        "depth": m.get("depth", "1"),
        "output": m.get("output", ""),
        "domain": m.get("domain", ""),
        "extra": m.get("extra_flags", ""),
    }


def find_wget():
    # prefer wget2 if available
    for name in ("wget2", "wget"):
        path = shutil.which(name)
        if path:
            return name
    print("Error: wget2 or wget not found on PATH.", file=sys.stderr)
    sys.exit(1)


def main():
    cfg = load_config()
    wget_cmd = find_wget()

    # 1) Get URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter URL to mirror: ").strip()
    if not url:
        print("No URL provided, exiting.", file=sys.stderr)
        sys.exit(1)

    # 2) Derive domain if not set
    domain = cfg["domain"] or urlparse(url).netloc

    # Create output directory if it doesn't exist
    output_dir = cfg["output"] or domain
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 3) Build command
    cmd = [
        wget_cmd,
        "--mirror",
        "--page-requisites",
        "--convert-links",
        "--no-parent",
        f"--level={cfg['depth']}",
        f"--domains={domain}",
        "-P",
        output_dir,
    ]

    # Handle SSL certificate issues
    if wget_cmd == "wget2":
        cmd.append("--no-check-certificate")  # For wget2
    else:
        cmd.append("--no-check-certificate")  # For wget

    # Handle special characters in URLs
    cmd.append(
        "--restrict-file-names=windows"
    )  # Handle special characters in filenames

    if cfg["extra"]:
        cmd += cfg["extra"].split()

    # Clean URL for display purposes only
    display_url = url if len(url) < 100 else url[:97] + "..."
    print(f"Downloading: {display_url}")
    print(f"Output directory: {output_dir}")

    cmd.append(url)

    print("Running:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
        print(f"\nSuccess! Website downloaded to: {os.path.abspath(output_dir)}")
    except subprocess.CalledProcessError as e:
        print(
            f"Error: wget command failed with exit code {e.returncode}", file=sys.stderr
        )
        print("Try simplifying the URL by removing query parameters", file=sys.stderr)

        # Offer to retry with simplified URL
        if (
            "?" in url
            and input(
                "Would you like to try again with a simplified URL? (y/n): "
            ).lower()
            == "y"
        ):
            simplified_url = url.split("?")[0]
            print(f"Retrying with: {simplified_url}")
            cmd[-1] = simplified_url  # Replace the URL in the command
            try:
                subprocess.run(cmd, check=True)
                print(
                    f"\nSuccess! Website downloaded to: {os.path.abspath(output_dir)}"
                )
            except subprocess.CalledProcessError:
                print("Error: Failed with simplified URL as well.", file=sys.stderr)

        sys.exit(1)


if __name__ == "__main__":
    main()
