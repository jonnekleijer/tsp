#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

METADATA_DELIMITER = ','
METADATA_DECIMAL = '.'

SURFACELEVEL = {'label': 'mv', 'linestyle': '--', 'color': 'lightgray', 'zorder': 2}

DEFAULTCOLOR = 'salmon'
DEFAULTCLUSTEREDFILEFORMAT = 'series_{name:}.png'
DEFAULTCLUSTEREDTITLEFORMAT = '{area:}: {name:}'
DEFAULTCLUSTEREDSIDETEXTFORMAT = 'mv: {surfacelev:6.1f} mNAP'
DEFAULTCLUSTEREDLABELFORMATS = {
    1: 'filter {filternr:}, {bottomfilter:.1f} - {topfilter:.1f} mNAP',
    2: '{label:} l{layer:d}',
}

DEFAULTSERIESFILEFORMAT = 'series_{name:}_{filternr:d}_l{layer:d}.png'
DEFAULTSERIESTITLEFORMAT = '{area:}: {name:} filter {filternr:d}, l{layer:d}'
DEFAULTSERIESSIDETEXTFORMAT = 'mv: {surfacelev:6.1f} mNAP\nbkf: {topfilter:6.1f} mNAP\nokf: {bottomfilter:6.1f} mNAP'

DEFAULTFIGSIZE = 11.7, 8.27
DEFAULTDPI = 200
