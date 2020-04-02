# gdc-maf-tool

## Aggregate GDC MAFs into one MAF file.

Installing
---

Requires Python 3.6 or later

```shell
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python setup.py install
```

Usage
---

```shell

$ gdc-maf-tool --help

usage: gdc-maf-tool [-h] [-p PROJECT_ID] [-f FILE_MANIFEST] [-c CASE_MANIFEST]
                    [-t TOKEN] [-o OUTPUT_FILENAME]

----GDC MAF Concatenation Tool v1.0----

optional arguments:
  -h, --help            show this help message and exit
  -p PROJECT_ID, --project PROJECT_ID
                        Project from which to gather MAF files.
  -f FILE_MANIFEST, --file-manifest FILE_MANIFEST
                        Specify MAF files with GDC Manifest
  -c CASE_MANIFEST, --case-manifest CASE_MANIFEST
                        Specify case ids associated with MAF files with GDC
                        Manifest
  -t TOKEN, --token TOKEN
                        GDC user token required for controlled access data
  -o OUTPUT_FILENAME, --output OUTPUT_FILENAME
                        Output file name for the resulting aggregate MAF.

$ # Downloading files from a project
$ gdc-maf-tool --project EXAMPLE-PROJECT

$ # Downloading specific files from a gdc manifest of file ids
$ gdc-maf-tool --file-manifest file-manifest.tsv

$ # Downloading specific files from a gdc manifest of case ids
$ gdc-maf-tool --case-manifest case-manifest.tsv

$ # Downloading controlled access data (that you have access to)
$ gdc-maf-tool --project EXAMPLE-PROJECT --token my-token.txt

$ # Choosing the resulting name gzipped name of your download
$ gdc-maf-tool --project EXAMPLE-PROJECT --output my-maf.maf.gz
```

Testing
---

```shell
$ tox
```

Contributing
---

We use `pre-commit` to enforce formatting and linting.  It needs to be installed 
in your local copy of this repo.

```shell script
pip install -r dev-requirements.txt
pre-commit install
```
