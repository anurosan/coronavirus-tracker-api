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
    
    exists = False
    
    for i in DATA_SOURCES:
        if DATA_SOURCES.index[i] == source:
            exists = True
   
    if exists == True:
        return DataSource.getService(source)
    else:
        return DataSource.getService("jhu")
