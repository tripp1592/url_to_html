#!/usr/bin/env python3
import configparser
import subprocess
import sys
import shutil
from urllib.parse import urlparse


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
        cfg["output"] or domain,
    ]
    if cfg["extra"]:
        cmd += cfg["extra"].split()

    cmd.append(url)

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
