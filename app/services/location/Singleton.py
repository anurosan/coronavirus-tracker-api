"""app.services.location.Singleton.py"""
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

LOGGER = logging.getLogger("services.location.Singleton")

class LocationServices(LocationService):
  async def get_all(self):
        # Get the locations.
        locations = await get_locations()
        return locations
      
  async def get(self, loc_id):  # pylint: disable=arguments-differ
        # Get location at the index equal to provided id.
        locations = await self.get_all()
        return locations[loc_id]
      
BASE_URL = "https://raw.githubusercontent.com/CSSEGISandData/2019-nCoV/master/csse_covid_19_data/csse_covid_19_time_series/"
something = "jhu"

@cached(cache=TTLCache(maxsize=1, ttl=1800))
async def createJHU():
    something = "jhu"
    data_id = "jhu.locations"
    LOGGER.info(f"pid:{PID}: {data_id} Requesting data...")

    confirmed = await get_category("confirmed")
    deaths = await get_category("deaths")
    recovered = await get_category("recovered")

    locations_confirmed = confirmed["locations"]
    locations_deaths = deaths["locations"]
    locations_recovered = recovered["locations"]

    locations = []
    for index, location in enumerate(locations_confirmed):
      key = (location["country"], location["province"])

      timelines = {
          "confirmed": location["history"],
          "deaths": parse_history(key, locations_deaths, index),
          "recovered": parse_history(key, locations_recovered, index),
      }

      coordinates = location["coordinates"]

      locations.append(
          TimelinedLocation(
                
              index,
              location["country"],
              location["province"],
        
              Coordinates(latitude=coordinates["lat"], longitude=coordinates["long"]),
              
              datetime.utcnow().isoformat() + "Z",
   
              {
                  "confirmed": Timeline(
                      timeline={
                          datetime.strptime(date, "%m/%d/%y").isoformat() + "Z": amount
                          for date, amount in timelines["confirmed"].items()
                      }
                  ),
                  "deaths": Timeline(
                      timeline={
                          datetime.strptime(date, "%m/%d/%y").isoformat() + "Z": amount
                          for date, amount in timelines["deaths"].items()
                      }
                  ),
                  "recovered": Timeline(
                      timeline={
                          datetime.strptime(date, "%m/%d/%y").isoformat() + "Z": amount
                          for date, amount in timelines["recovered"].items()
                      }
                  ),
              },
          )
      )
  LOGGER.info(f"{data_id} Data normalized")

  return locations
    
@cached(cache=TTLCache(maxsize=1, ttl=1800))
async def createCSBS():
  something = "csbs"
  BASE_URL = "https://facts.csbs.org/covid-19/covid19_county.csv"
  data_id = "csbs.locations"
  LOGGER.info(f"{data_id} Requesting data...")
  cache_results = await check_cache(data_id)
  if cache_results:
      LOGGER.info(f"{data_id} using shared cache results")
      locations = cache_results
  else:
      LOGGER.info(f"{data_id} shared cache empty")
      async with httputils.CLIENT_SESSION.get(BASE_URL) as response:
          text = await response.text()

      LOGGER.debug(f"{data_id} Data received")

      data = list(csv.DictReader(text.splitlines()))
      LOGGER.debug(f"{data_id} CSV parsed")

      locations = []

      for i, item in enumerate(data):
          state = item["State Name"]
          county = item["County Name"]

          if county in {"Unassigned", "Unknown"}:
              continue

          last_update = " ".join(item["Last Update"].split(" ")[0:2])

          locations.append(
              CSBSLocation(
                  i,
                  state,
                  county,
                  Coordinates(item["Latitude"], item["Longitude"]),
                  datetime.strptime(last_update, "%Y-%m-%d %H:%M").isoformat() + "Z",
                  int(item["Confirmed"] or 0),
                  int(item["Death"] or 0),
              )
          )
          
      LOGGER.info(f"{data_id} Data normalized")
      try:
          await load_cache(data_id, locations)
      except TypeError as type_err:
          LOGGER.error(type_err)

  return locations
    
@cached(cache=TTLCache(maxsize=1, ttl=1800))    
async def createNYT():
  something = "nyt"
  BASE_URL = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv" 
  data_id = "nyt.locations"
  LOGGER.info(f"{data_id} Requesting data...")
  cache_results = await check_cache(data_id)
  if cache_results:
      LOGGER.info(f"{data_id} using shared cache results")
      locations = cache_results
  else:
      LOGGER.info(f"{data_id} shared cache empty")
      async with httputils.CLIENT_SESSION.get(BASE_URL) as response:
          text = await response.text()
      LOGGER.debug(f"{data_id} Data received")

      data = list(csv.DictReader(text.splitlines()))
      LOGGER.debug(f"{data_id} CSV parsed")

      grouped_locations = get_grouped_locations_dict(data)

      locations = []

      for idx, (county_state, histories) in enumerate(grouped_locations.items()):
          confirmed_list = histories["confirmed"]
          confirmed_history = {date: int(amount or 0) for date, amount in confirmed_list}

          deaths_list = histories["deaths"]
          deaths_history = {date: int(amount or 0) for date, amount in deaths_list}

          locations.append(
              NYTLocation(
                  id=idx,
                  state=county_state[1],
                  county=county_state[0],
                  coordinates=Coordinates(None, None),  # NYT does not provide coordinates
                  last_updated=datetime.utcnow().isoformat() + "Z",  # since last request
                  timelines={
                      "confirmed": Timeline(
                          timeline={
                              datetime.strptime(date, "%Y-%m-%d").isoformat() + "Z": amount
                              for date, amount in confirmed_history.items()
                          }
                      ),
                      "deaths": Timeline(
                          timeline={
                              datetime.strptime(date, "%Y-%m-%d").isoformat() + "Z": amount
                              for date, amount in deaths_history.items()
                          }
                      ),
                      "recovered": Timeline(),
                  },
              )
          )
      LOGGER.info(f"{data_id} Data normalized")
      try:
          await load_cache(data_id, locations)
      except TypeError as type_err:
          LOGGER.error(type_err)

  return locations

def get_grouped_locations_dict(data):
    grouped_locations = {}

    # in increasing order of dates
    for row in data:
        county_state = (row["county"], row["state"])
        date = row["date"]
        confirmed = row["cases"]
        deaths = row["deaths"]

        # initialize if not existing
        if county_state not in grouped_locations:
            grouped_locations[county_state] = {"confirmed": [], "deaths": []}

        # append confirmed tuple to county_state (date, # confirmed)
        grouped_locations[county_state]["confirmed"].append((date, confirmed))
        # append deaths tuple to county_state (date, # deaths)
        grouped_locations[county_state]["deaths"].append((date, deaths))

    return grouped_locations

  def parse_history(key: tuple, locations: list, index: int):
    location_history = {}
    try:
        if key == (locations[index]["country"], locations[index]["province"]):
            location_history = locations[index]["history"]
    except (IndexError, KeyError):
        LOGGER.debug(f"iteration data merge error: {index} {key}")
    return location_history
  
@cached(cache=TTLCache(maxsize=4, ttl=1800))
async def get_category(category):
    """
    Retrieves the data for the provided category. The data is cached for 30 minutes locally, 1 hour via shared Redis.
    :returns: The data for category.
    :rtype: dict
    """
    # Adhere to category naming standard.
    category = category.lower()
    data_id = f"jhu.{category}"

    # check shared cache
    cache_results = await check_cache(data_id)
    if cache_results:
        LOGGER.info(f"{data_id} using shared cache results")
        results = cache_results
    else:
        LOGGER.info(f"{data_id} shared cache empty")
        # URL to request data from.
        url = BASE_URL + "time_series_covid19_%s_global.csv" % category

        # Request the data
        LOGGER.info(f"{data_id} Requesting data...")
        async with httputils.CLIENT_SESSION.get(url) as response:
            text = await response.text()

        LOGGER.debug(f"{data_id} Data received")

        # Parse the CSV.
        data = list(csv.DictReader(text.splitlines()))
        LOGGER.debug(f"{data_id} CSV parsed")

        # The normalized locations.
        locations = []

        for item in data:
            # Filter out all the dates.
            dates = dict(filter(lambda element: date_util.is_date(element[0]), item.items()))

            # Make location history from dates.
            history = {date: int(float(amount or 0)) for date, amount in dates.items()}

            # Country for this location.
            country = item["Country/Region"]

            # Latest data insert value.
            latest = list(history.values())[-1]

            # Normalize the item and append to locations.
            locations.append(
                {
                    # General info.
                    "country": country,
                    "country_code": countries.country_code(country),
                    "province": item["Province/State"],
                    # Coordinates.
                    "coordinates": {"lat": item["Lat"], "long": item["Long"],},
                    # History.
                    "history": history,
                    # Latest statistic.
                    "latest": int(latest or 0),
                }
            )
        LOGGER.debug(f"{data_id} Data normalized")

        # Latest total.
        latest = sum(map(lambda location: location["latest"], locations))

        # Return the final data.
        results = {
            "locations": locations,
            "latest": latest,
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "source": "https://github.com/ExpDev07/coronavirus-tracker-api",
        }
        # save the results to distributed cache
        await load_cache(data_id, results)

    LOGGER.info(f"{data_id} results:\n{pf(results, depth=1)}")
    return results

@cached(cache=TTLCache(maxsize=1, ttl=1800))
async def get_locations():
  thisTemp = LocationServices()
  if something == "nyt":
    return thisTemp.createNYT()
  elif something == "csbs":
    return thisTemp.createCSBS()
  else:
    return thisTemp.createJHU()
  
