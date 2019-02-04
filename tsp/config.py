#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from collections import ChainMap
from types import SimpleNamespace
import yaml
import os

thisfolder = os.path.dirname(os.path.realpath(__file__))
defaultconfigfile = r'config.yaml'
userconfigfile = r'..\userconfig.yaml'

defaultconfigfile = os.path.join(thisfolder, defaultconfigfile)
userconfigfile = os.path.join(thisfolder, userconfigfile)

with open(defaultconfigfile) as y:
    config_mapping = yaml.load(y)

if os.path.exists(userconfigfile):
    with open(userconfigfile) as y:
        userconfig_mapping = yaml.load(y)
    if userconfig_mapping is not None:
        config_mapping = ChainMap(userconfig_mapping, config_mapping)

config = SimpleNamespace(**config_mapping)
