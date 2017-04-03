#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from config import config

import pandas as pd

def cleaned(dirtystring):
    return (dirtystring
        .replace('(', '_')
        .replace(')', '_')
        .replace(',', '_')
        .replace('.', '_')
        .replace(' ', '_'))


def read_table(csvfile,
        delimiter=config.METADATA_DELIMITER,
        decimal=config.METADATA_DECIMAL,
        index_cols=[0, 1],
        header=0,
        na_values=None,):
    return pd.read_csv(csvfile,
        delimiter=delimiter,
        decimal=decimal,
        index_col=index_cols,
        header=0,
        na_values=na_values,
        )


def table_from_record(record,
        filefield='file',
        tablefield='table',
        namefield='name'):
    with pd.HDFStore(record.pop(filefield), 'r') as store:
        table = store[record.pop(tablefield)]
        table.name = record.pop(namefield)
        return table
