#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

# package
from tsp.config import config

# 3rd party
import pandas as pd

# std
import argparse
import logging
import yaml
import os

log = logging.getLogger(os.path.basename(__file__))


def get_parser():
    '''get argumentparser and add arguments'''
    parser = argparse.ArgumentParser(
        'read series in CSV file and write to H5 store',
    )

    # Command line arguments
    parser.add_argument('inputfile', type=str,
                        help=('YAML input file containing keyword arguments'))
    return parser


def run(**kwargs):
    # unpack input from kwargs
    csvfile = kwargs['csvfile']
    delimiter = kwargs.get('delimiter', config.DATA_DELIMITER)
    decimal = kwargs.get('decimal', config.DATA_DECIMAL)
    na_values = kwargs.get('na_values')
    datetimeformat = kwargs.get('datetimeformat', config.DATA_DATETIMEFORMAT)
    locationfield = kwargs['locationfield']
    filternrfield = kwargs['filternrfield']
    datetimefield = kwargs['datetimefield']
    valuefield = kwargs['valuefield']
    storefile = kwargs['storefile']
    tablename = kwargs.get('tablename', 'series')

    # read CSV file
    log.info('reading {file:}'.format(file=os.path.basename(csvfile)))
    index_cols = [locationfield, filternrfield]
    usecols = [locationfield, filternrfield, datetimefield, valuefield]
    table = pd.read_csv(csvfile,
                        delimiter=delimiter,
                        decimal=decimal,
                        index_col=index_cols,
                        header=0,
                        na_values=na_values,
                        usecols=usecols,
                        )

    # parse dates and append to index
    dates = pd.to_datetime(table.pop(datetimefield), format=datetimeformat)
    table.set_index(dates, append=True, inplace=True)

    # drop duplicates
    table = table.groupby(level=[0, 1, 2]).last()

    # select valuefield
    table = table.loc[:, valuefield]

    # sort index
    table = table.sort_index()

    # write to HDF5 store
    log.info('writing to store {}'.format(os.path.basename(storefile)))
    with pd.HDFStore(storefile) as store:
        store.put(tablename, table)


def main(inputfile=None):
    # arguments from input file
    if inputfile is None:
        args = get_parser().parse_args()
        inputfile = args.inputfile
    with open(inputfile) as y:
        kwargs = yaml.load(y)
        kwargs['inputfile'] = inputfile
    run(**kwargs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
