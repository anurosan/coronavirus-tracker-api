"""app.data"""

from ..services.location.Singleton import LocationService


def data_source(source):
    """
    Retrieves the provided data-source service.

    :returns: The service.
    :rtype: LocationService
    """
    
    location = LocationService()
    
    if source.lower() == "csbs":
        return location.createCSBS()
    elif source.lower() == "nyt":
        return location.createNYT()
    else:
        return location.createJHU()
    
