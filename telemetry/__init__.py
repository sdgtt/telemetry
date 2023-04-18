from telemetry.db import db
from telemetry.elastic import elastic
from telemetry.ingest import ingest
from telemetry.searches import searches
from telemetry.gargantua import Gargantua as gargantua
from telemetry.gparser import parser
from telemetry.gparser import grabber

import telemetry.prod as prod

"""Telemetry: Test Data Aggregator"""

__author__ = """Travis F. Collins"""
__email__ = "travis.collins@analog.com"
__version__ = "0.0.1"
name = "Telemetry"
