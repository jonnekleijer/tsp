#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

# package
from config import config
import utils

# 3rd party
import pandas as pd
import numpy as np

# std
from collections import OrderedDict
import argparse
import logging
import yaml
import os


def get_parser():
    '''get argumentparser and add arguments
    '''
    parser = argparse.ArgumentParser(
        'calculate statistics for observed and model timeseries',
        )

    # Command line arguments
    parser.add_argument('inputfile', type=str,
        help=('YAML input file containing keyword arguments'))
    return parser


def mean_error(residuals):
    return residuals.mean()


def mean_absolute_error(residuals):
    return residuals.abs().mean()


def root_mean_square_error(residuals):
    return np.sqrt(residuals.pow(2).mean())


def sum_of_squared_errors(residuals):
    return residuals.pow(2).sum()


def explained_variance_percentage(observed, residuals):
    return (observed.var() - residuals.var()) / observed.var() * 100.


def run(**kwargs):
    # unpack input from kwargs
    metadata = kwargs['metadata']
    observed = kwargs['observed']
    model = kwargs.get('model')
    period = kwargs.get('period')
    export_series = kwargs.get('export_series', False)
    exportfolder = kwargs['exportfolder']
    seriesfileformat = kwargs.get('seriesfileformat',
                                  config.SERIESFILEFORMAT)
    summaryfileformat = kwargs.get('summaryfileformat',
                                   config.SUMMARYFILEFORMAT)
    summarybylayerfileformat = kwargs.get('summarybylayerfileformat',
                                   config.SUMMARYBYLAYERFILEFORMAT)

    # create export folder if it does not exist
    if not os.path.exists(exportfolder):
        os.mkdir(exportfolder)

    # read metadata
    logging.info('reading metadata')
    metadatafile = metadata.pop('file')
    if metadatafile.lower().endswith('.h5'):
        with pd.HDFStore(metadata.pop('file')) as s:
            md = s[metadata.pop('table')]
    else:
        index_cols = metadata.pop('index_cols')
        md = utils.read_table(metadatafile, index_cols=index_cols)

    md = md.groupby(level=[0, 1]).last()

    areas = md.loc[:, metadata.pop('areafield')].astype(str)
    layers = md.loc[:, metadata.pop('layerfield')]

    # read series and attrs from records
    logging.info('reading observed timeseries')
    observed = utils.table_from_record(observed)

    # read series and attrs from records
    logging.info('reading model timeseries')
    model = utils.table_from_record(model)

    # convert period to datetime
    if period is not None:
        start, end = period
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)
        observedname = observed.name
        observed = (observed
                    .unstack(level=[0, 1])
                    .truncate(before=start, after=end)
                    .stack([0, 1])
                    .reorder_levels([1, 2, 0])
                    .sort_index())
        observed.name = observedname
        modelname = model.name
        model = (model
                    .unstack(level=[0, 1])
                    .truncate(before=start, after=end)
                    .stack([0, 1])
                    .reorder_levels([1, 2, 0])
                    .sort_index())
        model.name = modelname

    # calculate residuals
    logging.info('calculating residuals')
    residuals = model.reindex_like(observed, method='ffill') - observed
    residuals.name = 'r_{}'.format(model.name)

    # join observed, model and residuals
    series = pd.concat([observed, model, residuals], axis=1)

    # get start, end from index if not given
    if period is None:
        start = series.index[0][2]
        end = series.index[-1][2]

    # export series to CSV
    seriesfile = os.path.join(exportfolder, seriesfileformat.format(
        observed=observed.name,
        model=model.name,
        start=start.strftime('%Y%m%d%H%M%S'),
        end=end.strftime('%Y%m%d%H%M%S'),
        ))

    if export_series:
        logging.info('exporting series to {}'.format(
                 os.path.basename(seriesfile)))
        series.to_csv(seriesfile)

    # summary statistics
    statfuncs = OrderedDict([
        ('mean error', mean_error),
        ('mean absolute error', mean_absolute_error),
        ('root mean square error', root_mean_square_error),
        ])
    summary = residuals.groupby(level=[0, 1]).aggregate(statfuncs)

    evp = lambda s: explained_variance_percentage(s[observed.name],
                                                  s[residuals.name])
    summary['explained variance percentage'] = (series
                                                .groupby(level=(0, 1))
                                                .apply(evp))
    summary['nresiduals'] = residuals.groupby(level=[0, 1]).count()

    summaryfile = os.path.join(exportfolder, summaryfileformat.format(
        observed=observed.name,
        model=model.name,
        start=start.strftime('%Y%m%d%H%M%S'),
        end=end.strftime('%Y%m%d%H%M%S'),
        ))

    # export summary to CSV
    logging.info('exporting summary statistics to {}'.format(
                 os.path.basename(summaryfile)))
    summary.to_csv(summaryfile)

    # summary by layer
    layers = layers.reindex_like(residuals, method='ffill')
    summarybylayer = residuals.groupby(layers).aggregate(statfuncs)

    evp = lambda s: explained_variance_percentage(s[observed.name],
                                                  s[residuals.name])
    summarybylayer['explained variance percentage'] = (series
                                                        .groupby(layers)
                                                        .apply(evp))

    summarybylayer['nlocations'] = (residuals.groupby(layers)
                                .apply(lambda s: len(s.groupby(level=0))))
    summarybylayer['nfilters'] = (residuals.groupby(layers)
                                .apply(lambda s: len(s.groupby(level=[0, 1]))))
    summarybylayer['nresiduals'] = residuals.groupby(layers).count()

    summarybylayerfile = os.path.join(exportfolder,
        summarybylayerfileformat.format(
        observed=observed.name,
        model=model.name,
        start=start.strftime('%Y%m%d%H%M%S'),
        end=end.strftime('%Y%m%d%H%M%S'),
        ))

    # export summary by layer to CSV
    logging.info('exporting by layer statistics to {}'.format(
                 os.path.basename(summarybylayerfile)))
    summarybylayer.to_csv(summarybylayerfile)



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
