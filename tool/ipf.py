#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import utils

import numpy as np

import logging
import shlex
import os

# debugging
import pdb

log = logging.getLogger(os.path.basename(__file__))

def careful_float(value):
    """try to convert value to float"""
    try:
        return float(value)
    except ValueError:
        return np.nan


def read(textfile, converter=None, masked=True, fill=None, hastxt=True, delimiter=' '):
    """read iMOD format .txt or .ipf files"""
    log.info('reading {}'.format(os.path.basename(textfile)))
    converter = converter or {}
    with open(textfile) as f:
        line = lambda: f.readline().rstrip('\n')
        nrows = int(line())
        ncols = int(line())
        names = []
        nodatavalues = {}
        for j in range(ncols):
            name, *other = line().split(',')
            name = utils.cleaned(name)
            names.append(name)
            if len(other) > 0:
                nodatavalues[name] = converter.get(name,
                                                   careful_float)(other[0])
        # last line of columns
        if hastxt:
            seriescol, seriesext = line().split(',')
            seriescol = int(seriescol)
            seriesext = seriesext.lower()

        for i in range(nrows):
            if delimiter == ' ':
                values = [v for v in shlex.split(line())if v]
            else:
                values = [v for v in line().split(delimiter) if v]
            zipped_raw = zip(names, values)
            row_values = {n: converter.get(n, careful_float)(v)
                for n, v in zipped_raw}
            if masked:
                row_masked = {n: fill
                    if (n in nodatavalues and v == nodatavalues[n]) else v
                    for n, v in row_values.items()}
                yield row_masked
            else:
                yield row_values
