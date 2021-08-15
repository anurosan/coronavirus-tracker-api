"""app.services.location.locationFactory.py"""
import csv
import logging
import os
from datetime import datetime
from pprint import pformat as pf
from asyncache import cached
from cachetools import TTLCache

from ...caches import check_cache, load_cache
from ...coordinates import Coordinates
from ...location import TimelinedLocation
from ...location.csbs import CSBSLocation
from ...location.nyt import NYTLocation
from ...models import Timeline
from ...utils import countries
from ...utils import date as date_util
from ...utils import httputils
from . import LocationService

class LocationServiceFactory(LocationService):
  def createCSBS:
    #something
    s = 2
  def createCSBS:
    #something
    s = 1
  def createNYT:
    s = 3 
