#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV


# package
from config import config
import ipf
import utils

# 3rd party
import pandas as pd
import numpy as np

# std
import argparse
import logging
import yaml
import glob
import os

log = logging.getLogger(os.path.basename(__file__))


def get_parser():
    '''get argumentparser and add arguments'''
    parser = argparse.ArgumentParser(
        'read model series from folder with .txt files and write to H5 store',
        )

    # Command line arguments
    parser.add_argument('inputfile', type=str,
        help=('YAML input file containing keyword arguments'))
    return parser


def run(**kwargs):
    # unpack input from kwargs
    metadatafile = kwargs['metadatafile']
    locationfield = kwargs['locationfield']
    filternrfield = kwargs['filternrfield']
    modelidfield = kwargs['modelidfield']
    folder = kwargs['folder']
    fileformat = kwargs.get('fileformat', config.IPF_FILEFORMAT)
    datetimeformat = kwargs.get('datetimeformat', config.IPF_DATETIMEFORMAT)
    delimiter = kwargs.get('delimiter', config.IPF_DELIMITER)
    decimal = kwargs.get('decimal', config.IPF_DECIMAL)
    datetimefield = kwargs['datetimefield']
    valuefield = kwargs['valuefield']
    storefile = kwargs['storefile']
    tablename = kwargs.get('tablename', 'series')

    # read metadata
    index_cols = [locationfield, filternrfield]
    metadata = utils.read_table(metadatafile, index_cols=index_cols)
    modelids = metadata[modelidfield].dropna()

    tables = []
    for (location, filternr), modelid in modelids.iteritems():
        txtfile = os.path.join(folder, fileformat.format(
            modelid=modelid,
            ))
        if not os.path.exists(txtfile):
            log.warning(('no output for '
                'location {location:} filter {filternr:d},'
                'skipping..').format(
                location=location,
                filternr=filternr,
                ))
            continue
        log.info('location {location:} filter {filternr:d}'.format(
                location=location,
                filternr=filternr,
            ))
        records = ipf.read(txtfile,
            hastxt=False,
            delimiter=delimiter)
        table = pd.DataFrame(records)

        table['location'] = location
        table['filternr'] = filternr

        tables.append(table)

    if not len(tables) > 0:
        log.warning('no output files available, exiting..')
        return

    # merge to dataframe and set index
    table = pd.concat(tables, axis=0)
    log.info('converting timestamps to datetime')
    table['date_time'] = pd.to_datetime(table[datetimefield],
        format=datetimeformat)
    table.set_index(['location', 'filternr', 'date_time'],
        drop=True,
        inplace=True)

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


def main():
    # arguments from input file
    args = get_parser().parse_args()
    with open(args.inputfile) as y:
        kwargs = yaml.load(y)
        kwargs['inputfile'] = args.inputfile
    run(**kwargs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
