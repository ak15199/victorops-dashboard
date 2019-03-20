#!/usr/bin/env python

import os, sys
from os.path import dirname, realpath, join

path = join(dirname(realpath(__file__)), "app")
sys.path.append(path)

from application import app


app.run()
