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
    <a href="https://github.com/AWSToolbox/find-public-rds-snapshots/blob/master/.github/CODE_OF_CONDUCT.md">
        <img src="https://img.shields.io/badge/Code%20of%20Conduct-blue?style=for-the-badge" />
    </a>
    <a href="https://github.com/AWSToolbox/find-public-rds-snapshots/blob/master/.github/CONTRIBUTING.md">
        <img src="https://img.shields.io/badge/Contributing-blue?style=for-the-badge" />
    </a>
    <a href="https://github.com/AWSToolbox/find-public-rds-snapshots/blob/master/.github/SECURITY.md">
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

This tool will allow you to search for ALL public RDS snapshots based on a given regular expression (regex). The default regular expression is .* which means match everything.

Like most tools that could be exploited for nefarious means, we did think long and hard about wether we should release this tool or not, but we decided that most of the `bad actors` already have tools like this and this tool could be used by the `good guys` to protect themselves.

### Example Usage

The following example will search for all public RDS snapshots which contain the word `wolf software`.

```shell
./find-public-rds-snapshots.py -s 'wolf.+software'
```
> The search text is matched against the DBSnapshotIdentifier and the DBInstanceIdentifier. Please refer to the [AWS documentation](https://docs.aws.amazon.com/cli/latest/reference/rds/describe-db-snapshots.html) for more details.

## Usage

```shell
usage: find-public-rds-snapshots [-h] [-v] [-r REGIONS] [-s SEARCH] [-i] [-t] [-c] [-j] [-f FILENAME] [-S SORT_ORDER]

Locate any public rds snapshots

flags:
  -h, --help            show this help message and exit
  -v, --verbose         Account level output (default: False)

required arguments:
  -r REGIONS, --regions REGIONS
                        A comma separated list of regions to search (default: all)
  -s SEARCH, --search SEARCH
                        The search regex (default: .*)

optional arguments:
  -i, --case-insensitive
                        Make the search case insensitive (default: False)
  -t, --terminal        Draw a table of the results on the terminal (default: False)
  -c, --csv             Save the results as a csv formatted file (default: False)
  -j, --json            Save the results as a json formatted file (default: False)
  -f FILENAME, --filename FILENAME
                        The filename to save the results to (default: search-results)

sorting arguments:
  -S SORT_ORDER, --sort-order SORT_ORDER
                        Define the sort order of the results (E, R, S, T) (default: None)

Search Options: E=Database Engine, R=Region Name, S=Database Size, T=Creation Time.
Prefixing any of the above with an exclamation sign (!) will invert the order.
```

## Known Limitations

The script can only locate public RDS snapshots within regions to which your account credentials have access, so if a region is NOT enabled in your account then you will not see public RDS snapshots from that region.

If you want to see which regions you have access to, then we provide a tool for that also. [AWS List Regions](https://github.com/AWSToolbox/list-regions)
