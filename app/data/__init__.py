"""app.data"""

from ..services.location.Singleton import LocationServices


def data_source(source):
    """
    Retrieves the provided data-source service.

    :returns: The service.
    :rtype: LocationService
    """
    
    location = LocationServices()
    
    if source.lower() == "csbs":
        return location.createCSBS()
    elif source.lower() == "nyt":
        return location.createNYT()
    else:
        return location.createJHU()
    
