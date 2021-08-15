"""app.data"""
#from ..services.location.csbs import CSBSLocationService
#from ..services.location.jhu import JhuLocationService
#from ..services.location.nyt import NYTLocationService
from ..services.location.locationFactory import LocationServiceFactory

# Mapping of services to data-sources.
"""
DATA_SOURCES = {
    "jhu": JhuLocationService(),
    "csbs": CSBSLocationService(),
    "nyt": NYTLocationService(),
}
"""

def data_source(source):
    """
    Retrieves the provided data-source service.

    :returns: The service.
    :rtype: LocationService
    """
    
    location = LocationServiceFactory()
    
    if source.lower() = "csbs":
        return location.createCSBS()
    elif source.lower() = "nyt":
        return location.createNYT()
    else:
        return location.getDefault()
    
    #return DATA_SOURCES.get(source.lower())
