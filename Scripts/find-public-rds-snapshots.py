#!/usr/bin/env python

"""
Docs to follow
"""

import argparse
import csv
import json
import re
import sys
import warnings

from argparse import ArgumentParser, SUPPRESS
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import cmp_to_key
from operator import itemgetter

import colored
import botocore
import boto3

from colored import stylize
from prettytable import PrettyTable
from yaspin import yaspin

regions_in_flight = 0
region_total = 0


def save_results_as_csv(args, results):
    """
    Docs
    """
    with open(f'{args.filename}.csv', 'w', encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        columns = list({column for row in results for column in row.keys()})
        writer.writerow(columns)
        for row in results:
            writer.writerow([None if column not in row else row[column] for column in columns])


def save_results_as_json(args, results):
    """
    Docs
    """
    with open(f'{args.filename}.json', "w", encoding="utf-8") as outfile:
        json.dump(results, outfile, indent=4, default=str)


def print_table_of_results(results):
    """
    Docs
    """
    table = PrettyTable()

    table.field_names = [
                         'Region',
                         'Snapshot Identifier',
                         'Instance Identifier',
                         'Creation Time',
                         'Engine',
                         'Size'
                        ]

    for parts in results:
        table.add_row([
                       parts['Region'],
                       parts['DBSnapshotIdentifier'],
                       parts['DBInstanceIdentifier'],
                       parts['SnapshotCreateTimeFormatted'],
                       parts['Engine'],
                       parts['AllocatedStorage']
                      ])
    print(table)


def cmp(x, y):
    """
    Docs
    """
    return (x > y) - (x < y)


def multikeysort(items, columns):
    """
    Docs
    """
    comparers = [
        ((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1))
        for col in columns
    ]

    def comparer(left, right):
        comparer_iter = (
            cmp(fn(left), fn(right)) * mult
            for fn, mult in comparers
        )
        return next((result for result in comparer_iter if result), 0)
    return sorted(items, key=cmp_to_key(comparer))


def sort_results(args, results):
    """
    Docs
    """
    keys = []

    if args.sort_order:
        for order in args.sort_order.split(','):
            match order:
                case 'E':
                    keys.append('Engine')
                case '!E':
                    keys.append('-Engine')
                case 'R':
                    keys.append('Region')
                case '!R':
                    keys.append('-Region')
                case 'S':
                    keys.append('AllocatedStorage')
                case '!S':
                    keys.append('-AllocatedStorage')
                case 'T':
                    keys.append('SnapshotCreateTime')
                case '!T':
                    keys.append('-SnapshotCreateTime')
                case _:
                    print(stylize(f"{order} is an unknown options", colored.fg("yellow")))

        if len(keys) < 1:
            print(stylize("Warning: No valid options! - Aborting sort", colored.fg("yellow")))
            return results
        results = multikeysort(results, keys)
    return results


def process_results(args, results):
    """
    Docs
    """
    sorted_results = sort_results(args, results)

    if args.csv is True:
        save_results_as_csv(args, sorted_results)
    if args.json is True:
        save_results_as_json(args, sorted_results)
    if args.terminal is True:
        print_table_of_results(sorted_results)


def get_region_long_name(ssm, short_code):
    """
    something here
    """

    param_name = (f'/aws/service/global-infrastructure/regions/{short_code}/longName')
    response = ssm.get_parameters(Names=[param_name])
    return response['Parameters'][0]['Value']


def get_region_short_codes(ssm):
    """
    something here
    """

    output = set()
    for page in ssm.get_paginator('get_parameters_by_path').paginate(Path='/aws/service/global-infrastructure/regions'):
        output.update(p['Value'] for p in page['Parameters'])

    return output


def get_region_list():
    """
    something here
    """

    with yaspin(text=stylize("Generating Region List", colored.fg("green")), timer=True) as spinner:
        try:
            ssm = boto3.client('ssm')

            regions = {}
            for nsc in get_region_short_codes(ssm):
                regions[nsc] = get_region_long_name(ssm, nsc)

            sorted_regions = dict(sorted(regions.items()))
        except botocore.exceptions.ClientError:
            spinner.fail("💥")
            print(stylize("Fatal: The security token included in the request is invalid. - Aborting!", colored.fg("red")))
            sys.exit(0)

    spinner.ok("✅")
    return sorted_regions


def filter_region_list(args, all_regions):
    """
    Docs
    """
    filtered_regions = {}

    if args.regions == 'all':
        return all_regions

    regions_from_user = args.regions.split(',')

    for region in regions_from_user:
        if region in all_regions:
            filtered_regions[region] = all_regions[region]
        else:
            print(stylize(f"Warning: {region} is not a valid region - removing from region list", colored.fg("yellow")))
    return filtered_regions


def paginate(client, method, **kwargs):
    """
    docs
    """
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result


def get_rds_snapshots(args, region):
    """
    docs
    """
    results = []

    client = boto3.client('rds', region_name=region)

    try:
        rds_snapshots = paginate(client, client.describe_db_snapshots, IncludePublic=True, IncludeShared=False, SnapshotType='public')
        for snapshot in rds_snapshots:
            # Make sure it is available first
            if snapshot['Status'] == 'available':

                # Test DBSnapshotIdentifier and DBInstanceIdentifier
                if re.match(args.search, snapshot['DBSnapshotIdentifier'], re.IGNORECASE) or re.match(args.search, snapshot['DBInstanceIdentifier'], re.IGNORECASE):
                    # Add missing info
                    snapshot['Region'] = region
                    snapshot['SnapshotCreateTimeFormatted'] = snapshot['SnapshotCreateTime'].strftime("%-d %b %Y %X")
                    results.append(snapshot)
    except botocore.exceptions.ClientError:
        # These are regions that are not enabled so ignore and move on
        pass

    return results


def find_snapshots_per_region(region, args, spinner):
    """
    Docs
    """
    global regions_in_flight
    results = []

    regions_in_flight += 1
    if args.verbose is True:
        spinner.write(stylize(f"Region {region}: Search Started [{regions_in_flight} of {region_total}]", colored.fg("cyan")))

    results = get_rds_snapshots(args, region)

    regions_in_flight -= 1
    if args.verbose is True:
        spinner.write(stylize(f"Region {region}: Search Complete [{regions_in_flight} left to complete]", colored.fg("cyan")))

    return results


def find_snapshots(args):
    """
    Docs
    """
    global region_total
    threads = []
    results = []

    how_many = len(args.regions)
    region_total = how_many

    with yaspin(text=stylize(f"Processing Region List ({how_many} threads)", colored.fg("green")), timer=True) as spinner:
        with ThreadPoolExecutor(max_workers=how_many) as executor:
            for region in args.regions:
                threads.append(executor.submit(find_snapshots_per_region, region, args, spinner))

            for task in as_completed(threads):
                thread_results = task.result()
                if thread_results:
                    results += thread_results

    spinner.ok("✅")
    return results


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """
    Docs
    """
    pass


def setup_arg_parser():
    """
    Setup the arguments parser to handle the user input from the command line.
    """

    epilog = "Search Options: E=Database Engine, R=Region Name, S=Databse Size, T=Creation Time.\nPrefixing any of the above with an exclamation sign (!) will invert the order."

    parser = ArgumentParser(prog='find-public-rds-snapshots', description='Locate any public rds snapshots', add_help=False, epilog=epilog, formatter_class=CustomFormatter)
    flags = parser.add_argument_group('flags')
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    sorting = parser.add_argument_group('sorting arguments')

    flags.add_argument('-h', '--help', action='help', default=SUPPRESS, help='show this help message and exit')
    flags.add_argument('-v', '--verbose', action="store_true", help="Account level output", default=False)

    required.add_argument('-r', '--regions', type=str, help='A comma seperated list of regions to search', default='all')
    required.add_argument('-s', '--search', type=str, help='The search regex', default='.*')

    optional.add_argument('-t', '--terminal', action="store_true", help="Draw a table of the results on the terminal", default=False)
    optional.add_argument('-c', '--csv', action="store_true", help="Save the results as a csv formatted file", default=False)
    optional.add_argument('-j', '--json', action="store_true", help="Save the results as a json formarted file", default=False)
    optional.add_argument('-f', '--filename', type=str, help='The filename to save the results to', default='search-results')

    sorting.add_argument('-S', '--sort-order', type=str, help="Define the sort order of the results (E,R,S,T)")

    return parser


def process_arguments():
    """
    Main wrapper for handling the arguments, setup, read and valiate all before returning to main().
    """

    parser = setup_arg_parser()
    args = parser.parse_args()

    try:
        re.compile(args.search)
    except re.error:
        print(stylize(f"Error: {args.search} is not a valid regex patternh - Aborting!", colored.fg("red")))
        sys.exit(0)

    # This sis the slowest part - so lets do this last
    all_regions = get_region_list()
    args.regions = filter_region_list(args, all_regions)

    return args


def main():
    """
    The main function.
    """
    warnings.simplefilter(action='ignore', category=FutureWarning)

    args = process_arguments()

    if len(args.regions) < 1:
        print(stylize("Error: No valid regions found to search - Aborting!", colored.fg("red")))
        sys.exit(0)

    results = find_snapshots(args)
    print(stylize(f"Results: {len(results)} snapshots located using pattern {args.search}", colored.fg("green")))

    process_results(args, results)


if __name__ == "__main__":
    main()
