"""app.data"""
from ..services.location.csbs import CSBSLocationService
from ..services.location.jhu import JhuLocationService
from ..services.location.nyt import NYTLocationService
from app.data.dataSource import DataSource

DATA_SOURCES = ["jhu","csbs","nyt"]

def data_source(source):
    """
    Retrieves the provided data-source service.

    :returns: The service.
    :rtype: LocationService
    """   
    return DataSource.getService(source)
