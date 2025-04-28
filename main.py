#!/usr/bin/env python3
import configparser
import subprocess
import sys
import shutil
import os
import signal
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


def get_output_path(url, base_output_dir):
    """Create and return an output directory path based on the domain name."""
    # Extract domain from URL
    domain = urlparse(url).netloc

    # Clean domain name for use as directory name
    # Replace special characters that might cause issues in filenames
    domain = domain.replace(":", "_").replace("/", "_")

    # Always use "output" as the base directory if none specified
    if not base_output_dir:
        base_output_dir = "output"

    output_dir = os.path.join(base_output_dir, domain)

    # Create the directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return output_dir


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

    # Create website-specific output directory
    base_output_dir = cfg["output"]
    output_dir = get_output_path(url, base_output_dir)

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
        # Use Popen instead of run for better control
        process = subprocess.Popen(cmd)

        try:
            print("\nDownload in progress... Press Ctrl+C once to gracefully stop.")
            return_code = process.wait()

            if return_code == 0:
                print(
                    f"\nSuccess! Website downloaded to: {os.path.abspath(output_dir)}"
                )
            else:
                print(
                    f"Error: wget command failed with exit code {return_code}",
                    file=sys.stderr,
                )
                handle_error(url, cmd, output_dir)

        except KeyboardInterrupt:
            print("\nInterruption detected. Terminating wget gracefully...")
            # On Windows, use CTRL_C_EVENT instead of SIGTERM
            if os.name == "nt":
                process.send_signal(signal.CTRL_C_EVENT)
            else:
                process.terminate()  # SIGTERM

            # Wait for process to terminate with timeout
            try:
                process.wait(timeout=10)
                print("Download stopped. Partial content saved in output directory.")
            except subprocess.TimeoutExpired:
                print("wget did not terminate gracefully. Forcing termination...")
                process.kill()

            print(f"Partial download available in: {os.path.abspath(output_dir)}")
            return

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        handle_error(url, cmd, output_dir)


def handle_error(url, cmd, output_dir):
    """Handle error cases with helpful suggestions."""
    print("Try simplifying the URL by removing query parameters", file=sys.stderr)

    # Offer to retry with simplified URL
    if (
        "?" in url
        and input("Would you like to try again with a simplified URL? (y/n): ").lower()
        == "y"
    ):
        simplified_url = url.split("?")[0]
        print(f"Retrying with: {simplified_url}")
        cmd[-1] = simplified_url  # Replace the URL in the command
        try:
            # Use Popen for the retry as well
            retry_process = subprocess.Popen(cmd)
            try:
                print("\nDownload in progress... Press Ctrl+C once to gracefully stop.")
                return_code = retry_process.wait()

                if return_code == 0:
                    print(
                        f"\nSuccess! Website downloaded to: {os.path.abspath(output_dir)}"
                    )
                    return
            except KeyboardInterrupt:
                print("\nInterruption detected. Terminating wget gracefully...")
                if os.name == "nt":
                    retry_process.send_signal(signal.CTRL_C_EVENT)
                else:
                    retry_process.terminate()

                try:
                    retry_process.wait(timeout=10)
                    print(
                        "Download stopped. Partial content saved in output directory."
                    )
                except subprocess.TimeoutExpired:
                    print("wget did not terminate gracefully. Forcing termination...")
                    retry_process.kill()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            print("Error: Failed with simplified URL as well.", file=sys.stderr)

    # Additional troubleshooting suggestions
    print("\nTroubleshooting suggestions:")
    print("1. Try with a lower depth value in config.ini")
    print("2. Check your internet connection")
    print("3. The website might be blocking automated downloads")
    print("4. Add '--wait=1' to extra_flags in config.ini to slow down requests")

    sys.exit(1)


if __name__ == "__main__":
    main()
