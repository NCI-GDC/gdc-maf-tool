# gdc-maf-tool

## Aggregate GDC MAFs into one MAF file

The GDC MAF tool aggregates aliquot-level MAFs, which originate from one tumor-normal pair.  MAFs can aggregated on a project-level or by providing a set of files/cases. Note that currently the GDC MAF tool only supports Ensemble aliquot-level MAFs generated from whole exome sequencing.  Ensemble aliquot-level MAFs include variants from all five variant callers (MuTect2, MuSE, Varscan2, SomaticSniper, Pindel) and include information about which caller each variant originated from. The GDC MAF tool will only aggregate MAFs from within one GDC project.

### Querying for MAFs

Ensemble aliquot-level MAFs can be queried at the GDC Data Portal (https://portal.gdc.cancer.gov/repository) using the following filters along with the project of your choice:

* Data Format: maf
* Workflow Type: Aliquot Ensemble Somatic Variant Merging and Masking

Alternatively, this data set can be accessed at the following link:
https://portal.gdc.cancer.gov/repository?filters=%7B%22op%22%3A%22and%22%2C%22content%22%3A%5B%7B%22op%22%3A%22in%22%2C%22content%22%3A%7B%22field%22%3A%22files.analysis.workflow_type%22%2C%22value%22%3A%5B%22Aliquot+Ensemble+Somatic+Variant+Merging+and+Masking%22%5D%7D%7D%2C%7B%22op%22%3A%22in%22%2C%22content%22%3A%7B%22field%22%3A%22files.data_format%22%2C%22value%22%3A%5B%22maf%22%5D%7D%7D%5D%7D

To pass a set of files to this tool, query the desired files and download a GDC Manifest. This can be done by doing any of the following:

- Adding all required files to the cart, going to the cart, and choosing "Download" --> "Manifest"
- Choosing the "Manifest" button in the repository itself at the top of the list of files. 

### Querying for Cases

This tool can also aggregate the MAF files specified above for a custom set of cases from the GDC.  A list of cases can be retrieved from the GDC Data Portal by performing the following steps:

1.  Go to the GDC Exploration page: https://portal.gdc.cancer.gov/exploration
1.  Filter for a set of desired cases using the faceted search.
1.  Choose "Save/Edit Case Set" --> "Save as new case set"
1.  Once the set is saved, go to "Manage Sets" at the top of the Portal
1.  Choose "Export TSV" icon for the desired set. This should download a list of case UUIDs.


Installing
---

Requires Git and Python 3.6 or later.

#### Clone the repo:
```shell
$ git clone https://github.com/NCI-GDC/gdc-maf-tool.git
```
#### Create a virtualenv:
For Linux and Macos:
```shell
$ python3 -m venv venv
$ source venv/bin/activate
```
For Windows:
```shell
$ py -m venv venv
$ .\venv\Scripts\activate
```
#### Install the tool in the virtualenv:
```shell
$ pip install -r requirements.txt
$ python setup.py install
```

Usage
---

```shell

$ gdc-maf-tool --help

usage: gdc-maf-tool [-h] (-p PROJECT_ID | -f FILE_MANIFEST | -c CASE_MANIFEST)
                    [-t TOKEN] [-o OUTPUT_FILENAME]

----GDC MAF Concatenation Tool v0.0.3----

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
                        Output file name for the resulting aggregate MAF
                        (default: outfile.maf.gz).

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
