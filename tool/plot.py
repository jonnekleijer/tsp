#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

# package
import config
import utils

# 3rd party
from matplotlib import pyplot as plt
from matplotlib import rcParams
from matplotlib import dates
from matplotlib import ticker
import pandas as pd

# std
import argparse
import logging
import yaml
import os

plt.style.use('classic')

rcParams.update({
    'font.family': 'arial',
    'font.size': 8,
    'figure.subplot.hspace': 0.1,
    'figure.dpi': 200
    })

LOCATORS = {
    'y': dates.YearLocator,
    'm': dates.MonthLocator,
    'd': dates.DayLocator,
}

def get_parser():
    '''get argumentparser and add arguments
    '''
    parser = argparse.ArgumentParser(
        'plot timeseries figures',
        )

    # Command line arguments
    parser.add_argument('inputfile', type=str,
        help=('YAML input file containing keyword arguments'))
    return parser


def plot(imagefile,
    timeseries,
    attrs,
    figsize=None,
    dpi=200,
    period=None,
    xmajortickfrequency=None,
    xminortickfrequency=None,
    ylim=None,
    ymargin=None,
    ymajortickspacing=None,
    yminortickspacing=None,
    xlabel=None,
    ylabel=None,
    title=None,
    sidetext=None,
    surfacelevel=None,
    ):
    """Summary
    Plot columns of datetime indexed dataframe to imagefile.
    Accepts a number of optional formatting arguments.

    Args:
        imagefile (str): Path to destination file
        timeseries (DataFrame): Pandas Dataframe with datetime index
        attrs (dict): dict of plot attributes (color, linestyle, etc.) by label
        figsize (None, optional): Description
        dpi
        period (None, optional): Description
        xmajortickfrequency (None, optional): Description
        xminortickfrequency (None, optional): Description
        ylim (None, optional): Description
        ymargin (None, optional): Description
        ymajortickspacing (None, optional): Description
        yminortickspacing (None, optional): Description
        xlabel (None, optional): Description
        ylabel (None, optional): Description
        title (None, optional): Description
        sidetext (None, optional): Description

    Returns:
        TYPE: Description
    """
    if figsize is None:
        fig, ax = plt.subplots()
    else:
        fig, ax = plt.subplots(figsize=figsize)
    bxa = []

    for label, series in timeseries.items():
        series = series.dropna()
        if len(series) > 0:
            ax.plot(series, **attrs[label])

    ylim
    if surfacelevel is not None:
        ax.axhline(surfacelevel, **config.SURFACELEVEL)

    ax.grid(b=True, which='major', axis='both', color='k')

    if xmajortickfrequency is not None:
        freq = xmajortickfrequency[-1]
        try:
            base = int(xmajortickfrequency[:-1])
        except:
            base = 1
        locator = LOCATORS.get(freq)
        if locator is not None:
            if freq == 'y':
                loc = locator(base=base)
            elif freq == 'm':
                loc = locator(bymonth=range(1, 13, base))
            elif freq == 'd':
                loc = locator(byday=range(1, 13, base))
            ax.xaxis.set_major_locator(loc)

    if xminortickfrequency is not None:
        freq = xminortickfrequency[-1]
        try:
            base = int(xminortickfrequency[:-1])
        except:
            base = 1
        locator = LOCATORS.get(freq)
        if locator is not None:
            if freq == 'y':
                loc = locator(base=base)
            elif freq == 'm':
                loc = locator(bymonth=range(1, 13, base))
            elif freq == 'd':
                loc = locator(byday=range(1, 13, base))
            ax.xaxis.set_minor_locator(loc)
            ax.grid(b=True, which='minor', axis='x', color='lightgray')

    if ymajortickspacing is not None:
        loc = ticker.MultipleLocator(base=ymajortickspacing)
        ax.yaxis.set_major_locator(loc)

    if yminortickspacing is not None:
        loc = ticker.MultipleLocator(base=yminortickspacing)
        ax.yaxis.set_minor_locator(loc)
        ax.grid(b=True, which='minor', axis='y', color='lightgray')

    if ylim is not None:
        ax.set_ylim(ylim)
    elif ymargin is not None:
        ax.set_ymargin(ymargin)
        ax.autoscale()

    if period is not None:
        ax.set_xlim(period)

    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)

    lgd = ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    bxa.append(lgd)

    if title is not None:
        ttl = ax.set_title(title, fontsize=10)
        bxa.append(ttl)

    if sidetext is not None:
        sdt = ax.text(1.01, 0.5, sidetext, transform=ax.transAxes, fontsize=9)
        bxa.append(sdt)

    plt.savefig(imagefile, bbox_inches='tight',
        bbox_extra_artists=bxa, dpi=dpi)
    plt.close()


def run(**kwargs):
    # unpack input from kwargs
    metadata = kwargs['metadata']
    records = kwargs['records']
    resample_freq = kwargs.get('resample_freq')
    period = kwargs.get('period')
    xmajortickfrequency = kwargs.get('xmajortickfrequency')
    xminortickfrequency = kwargs.get('xminortickfrequency')
    ylim = kwargs.get('ylim')
    ymargin = kwargs.get('ymargin')
    ymajortickspacing = kwargs.get('ymajortickspacing')
    yminortickspacing = kwargs.get('yminortickspacing')
    xlabel = kwargs.get('xlabel')
    ylabel = kwargs.get('ylabel')
    exportfolder = kwargs['exportfolder']
    fileformat = kwargs.get('fileformat')
    titleformat = kwargs.get('titleformat')
    sidetextformat = kwargs.get('sidetextformat')
    serieslabelformats = kwargs.get('labelformat')
    figsize = kwargs.get('figsize', config.DEFAULTFIGSIZE)
    dpi = kwargs.get('dpi', config.DEFAULTDPI)
    plot_surfacelevel = kwargs.get('plot_surfacelevel', True)
    testone = kwargs.get('testone', False)
    clustered = kwargs.get('clustered', False)

    # create export folder if it does not exist
    if not os.path.exists(exportfolder):
        os.mkdir(exportfolder)

    # set default string formats
    if clustered:
        fileformat = fileformat or config.DEFAULTCLUSTEREDFILEFORMAT
        titleformat = titleformat or config.DEFAULTCLUSTEREDTITLEFORMAT
        sidetextformat = sidetextformat or config.DEFAULTCLUSTEREDSIDETEXTFORMAT
        serieslabelformats = serieslabelformats or config.DEFAULTCLUSTEREDLABELFORMATS
    else:
        fileformat = fileformat or config.DEFAULTSERIESFILEFORMAT
        titleformat = titleformat or config.DEFAULTSERIESTITLEFORMAT
        sidetextformat = sidetextformat or config.DEFAULTSERIESSIDETEXTFORMAT
        serieslabelformats = None

    # read metadata
    logging.info('reading metadata')
    if metadata['file'].lower().endswith('.h5'):
        md = utils.table_from_record(metadata)
    else:
        index_cols = metadata.pop('index_cols')
        md = utils.read_table(metadata['file'], index_cols=index_cols)

    md = md.groupby(level=[0, 1]).last()

    areas = md.loc[:, metadata.pop('areafield')].astype(str)
    layers = md.loc[:, metadata.pop('layerfield')]
    sidevars = md.loc[:, metadata.pop('sidefields')]
    if clustered:
        labelvars = md.loc[:, metadata.pop('labelfields')]
        areas = areas.groupby(level=0).first()
        sidevars = sidevars.groupby(level=0).first()

    # read series and attrs from records
    logging.info('reading timeseries')
    ss = {r['label']: utils.table_from_record(r) for r in records}
    ss = pd.DataFrame(ss)
    attrs = {r.pop('label'): r for r in records}

    # convert period to datetime
    if period is not None:
        start, end = period
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)
        period = (start, end)

    # resample series
    if (resample_freq is not None) and (period is not None):
        logging.info('resampling and truncating timeseries')
        ss = (ss
            .unstack(level=[0, 1])
            .resample(resample_freq)
            .first() # get first value in each period
            .truncate(before=start, after=end)
            .stack([1, 2])
            .reorder_levels([1, 2, 0])
            .sort_index())
    elif resample_freq is not None:
        logging.info('resampling timeseries')
        ss = (ss
            .unstack(level=[0, 1])
            .resample(resample_freq)
            .first() # get first value in each period
            .stack([1, 2])
            .reorder_levels([1, 2, 0])
            .sort_index())
    elif period is not None:
        logging.info('truncating timeseries')
        ss = (ss
            .unstack(level=[0, 1])
            .truncate(before=start, after=end)
            .stack([1, 2])
            .reorder_levels([1, 2, 0])
            .sort_index())

    if testone:
        if clustered:
            _, ss = next(iter(ss.groupby(level=[0,])))
        else:
            _, ss = next(iter(ss.groupby(level=[0, 1])))

    if clustered:
        for name, timeseries in ss.groupby(level=[0,]):
            logging.info('plotting {name:}'.format(
                name=name))
            timeseries.reset_index(level=[0,], drop=True, inplace=True)
            timeseries = timeseries.unstack(0)

            # relabel columns
            relabeled = []
            re_attrs = {}
            for label, filternr in timeseries.columns:
                layer = layers.loc[(name, filternr)]
                label_attrs = attrs[label].copy()
                colorsbylayer = label_attrs.pop('colorsbylayer')
                label_attrs['color'] = colorsbylayer.get(layer, config.DEFAULTCOLOR)
                formatnumber = label_attrs.pop('labelformat')
                labelformat = serieslabelformats.get(formatnumber, 1)
                relabel = labelformat.format(filternr=filternr, label=label,
                    layer=layer, **labelvars.loc[(name, filternr)])
                re_attrs[relabel] = label_attrs
                relabeled.append(relabel)
            timeseries.columns = relabeled

            # get area name
            area = areas.loc[name]

            # create file path
            areafolder = os.path.join(exportfolder, utils.cleaned(area))
            if not os.path.exists(areafolder):
                os.mkdir(areafolder)
            imagefile = os.path.join(areafolder, fileformat.format(
                area=utils.cleaned(area),
                name=name,))

            # format title
            title = titleformat.format(area=area, name=name)

            # format sidetext
            sidetext = sidetextformat.format(**sidevars.loc[name])

            # get surface level
            if plot_surfacelevel:
                surfacelevel = sidevars.loc[name, 'surfacelev']
            else:
                surfacelevel = None

            # plot
            plot(imagefile, timeseries, re_attrs,
                figsize=figsize,
                period=period,
                xmajortickfrequency=xmajortickfrequency,
                xminortickfrequency=xminortickfrequency,
                ylim=ylim,
                ymargin=ymargin,
                ymajortickspacing=ymajortickspacing,
                yminortickspacing=yminortickspacing,
                xlabel=xlabel,
                ylabel=ylabel,
                title=title,
                sidetext=sidetext,
                surfacelevel=surfacelevel,
                )
    else:
        for (name, filternr), timeseries in ss.groupby(level=[0, 1]):
            logging.info('plotting {name:} filter {filternr:d}'.format(
                name=name, filternr=filternr))
            timeseries.reset_index(level=[0, 1], drop=True, inplace=True)

            # get area name
            area = areas.loc[(name, filternr)]

            # get layer number
            layer = layers.loc[(name, filternr)]

            # create file path
            areafolder = os.path.join(exportfolder, utils.cleaned(area))
            if not os.path.exists(areafolder):
                os.mkdir(areafolder)
            imagefile = os.path.join(areafolder, fileformat.format(
                area=utils.cleaned(area),
                name=name, filternr=filternr, layer=layer))

            # format title
            title = titleformat.format(
                area=area, name=name, filternr=filternr, layer=layer)

            # format sidetext
            sidetext = sidetextformat.format(**sidevars.loc[(name, filternr)])

            # get surface level
            if plot_surfacelevel:
                surfacelevel = sidevars.loc[(name, filternr), 'surfacelev']
            else:
                surfacelevel = None

            # plot
            plot(imagefile, timeseries, attrs,
                figsize=figsize,
                dpi=dpi,
                period=period,
                xmajortickfrequency=xmajortickfrequency,
                xminortickfrequency=xminortickfrequency,
                ylim=ylim,
                ymargin=ymargin,
                ymajortickspacing=ymajortickspacing,
                yminortickspacing=yminortickspacing,
                xlabel=xlabel,
                ylabel=ylabel,
                title=title,
                sidetext=sidetext,
                surfacelevel=surfacelevel,
                )


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
