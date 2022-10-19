<p align="center">
    <a href="https://github.com/AWSToolbox/">
        <img src="https://cdn.wolfsoftware.com/assets/images/github/organisations/awstoolbox/black-and-white-circle-256.png" alt="AWSToolbox logo" />
    </a>
    <br />
    <a href="https://github.com/AWSToolbox/find-public-rds-snapshots/actions/workflows/cicd-pipeline.yml">
        <img src="https://img.shields.io/github/workflow/status/AWSToolbox/find-public-rds-snapshots/CICD%20Pipeline/master?style=for-the-badge" alt="Github Build Status">
    </a>
    <a href="https://github.com/AWSToolbox/find-public-rds-snapshots/releases/latest">
        <img src="https://img.shields.io/github/v/release/AWSToolbox/find-public-rds-snapshots?color=blue&label=Latest%20Release&style=for-the-badge" alt="Release">
    </a>
    <a href="https://github.com/AWSToolbox/find-public-rds-snapshots/releases/latest">
        <img src="https://img.shields.io/github/commits-since/AWSToolbox/find-public-rds-snapshots/latest.svg?color=blue&style=for-the-badge" alt="Commits since release">
    </a>
    <br />
    <a href=".github/CODE_OF_CONDUCT.md">
        <img src="https://img.shields.io/badge/Code%20of%20Conduct-blue?style=for-the-badge" />
    </a>
    <a href=".github/CONTRIBUTING.md">
        <img src="https://img.shields.io/badge/Contributing-blue?style=for-the-badge" />
    </a>
    <a href=".github/SECURITY.md">
        <img src="https://img.shields.io/badge/Report%20Security%20Concern-blue?style=for-the-badge" />
    </a>
    <a href="https://github.com/AWSToolbox/find-public-rds-snapshots/issues">
        <img src="https://img.shields.io/badge/Get%20Support-blue?style=for-the-badge" />
    </a>
    <br />
    <a href="https://wolfsoftware.com/">
        <img src="https://img.shields.io/badge/Created%20by%20Wolf%20Software-blue?style=for-the-badge" />
    </a>
</p>

## Overview


## Usage

```shell
usage: find-public-rds-snapshots [-h] [-v] [-r REGIONS] [-s SEARCH] [-t] [-c] [-j] [-f FILENAME] [-S SORT_ORDER]

Locate any public rds snapshots

flags:
  -h, --help            show this help message and exit
  -v, --verbose         Account level output (default: False)

required arguments:
  -r REGIONS, --regions REGIONS
                        A comma seperated list of regions to search (default: all)
  -s SEARCH, --search SEARCH
                        The search regex (default: .*)

optional arguments:
  -t, --terminal        Draw a table of the results on the terminal (default: False)
  -c, --csv             Save the results as a csv formatted file (default: False)
  -j, --json            Save the results as a json formarted file (default: False)
  -f FILENAME, --filename FILENAME
                        The filename to save the results to (default: search-results)

sorting arguments:
  -S SORT_ORDER, --sort-order SORT_ORDER
                        Define the sort order of the results (E,R,S,T) (default: None)

Search Options: E=Database Engine, R=Region Name, S=Databse Size, T=Creation Time.
Prefixing any of the above with an exclamation sign (!) will invert the order.

```
