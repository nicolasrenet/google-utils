## Purpose

Retrieve Google appfiles from a locally mounted Google-drive, while storing them in MS or OpenDocument formats.

 
+ `google-appfiles-download-simple.py` relies on HTTP and the `gdown` utility to retrieve the files: it is convenient to use, but fail on files that ...
+ `google-appfiles-download.py` is more robust, working on all but the largest files: however, since it uses the Google API, it requires a Google authentication and acquiring a authorization key.


## Usage

```bash
./google-appfiles-download.py <locally mounted google drive folder path>
```

## TODO:

+ because it uses the API, acquiring a key is necessary before using the script: should use Gdown instead to retrieve the file through HTTP.

