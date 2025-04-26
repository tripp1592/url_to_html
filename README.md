# URL to HTML Downloader

A simple yet powerful utility to download websites as local HTML files with all assets for offline viewing.

## Features

- Downloads complete websites with all necessary resources (CSS, JS, images)
- Converts links to work locally
- Configurable download depth
- Domain restriction to prevent unwanted external content
- Customizable output directory
- Support for both wget and wget2 (prefers wget2 if available)

## Requirements

- Python 3.6+
- wget or wget2 installed and available in your PATH

## Installation

1. Clone this repository or download the files
2. Install wget or wget2 if not already installed:
   - Windows: Download from [GNU Wget](https://www.gnu.org/software/wget/) or use [Chocolatey](https://chocolatey.org/) with `choco install wget`
   - macOS: Install with Homebrew using `brew install wget`
   - Linux: Install with your package manager, e.g., `apt install wget`

## Usage

### Basic Usage

Run the script and enter the URL when prompted:

```bash
python main.py
```

Or provide the URL as a command-line argument:

```bash
python main.py https://example.com
```

### Configuration

The script uses `config.ini` for configuration. Here's what you can customize:

```ini
[mirror]
depth = 2                                  # How many levels deep to crawl
output = output                            # Output directory
domain =                                   # Restrict to specific domain (default: derived from URL)
extra_flags = --adjust-extension --reject=pdf -nH  # Additional wget flags
```

## Common Extra Flags

- `--adjust-extension`: Add appropriate file extensions based on content type
- `-nH`: Don't create host directories
- `--reject=pdf`: Don't download PDF files
- `--exclude-directories=dir1,dir2`: Skip specified directories
- `--timeout=10`: Set timeout for connections

## Example

To download the Python Packaging tutorial:

```bash
python main.py https://py-pkgs.org/
```

This will create an `output` directory containing all HTML files and assets needed to browse the site offline.

## License

This project is open source and available under the [MIT License](LICENSE).