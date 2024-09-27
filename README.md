## Purpose

Retrieve Google appfiles from a locally mounted Google-drive, while storing them in MS or OpenDocument formats.

 
+ `google-appfiles-download-simple.py` relies on HTTP and the `gdown` utility to retrieve the files: it is convenient to use, but fail on files that do not have the necessary permissions.
+ `google-appfiles-download.py` is more robust, working on all but the largest files: however, since it uses the Google API, it requires a Google authentication and acquiring an authorization key.


## Usage

### Gdown-based version:

```bash
Usage: ./google-appfiles-download-simple.py [-h] [-n] google_pathname [google_pathname ...]
```

```bash
usage: ./google-appfiles-download.py [-h] [-n] google_pathname [google_pathname ...]
```

where:

+ positional arguments:
  `google_pathname`  A "*.desktop" file or folder path.

+ optional arguments:
  `-h`, `--help`       show this help message and exit
  `-n`, `--dry-run`    List the files that would be downloaded instead.

