from ..services.location.csbs import CSBSLocationService
from ..services.location.jhu import JhuLocationService
from ..services.location.nyt import NYTLocationService

class DataSource():
  def getService(source):
    if source.lower() == "csbs":
      temp = CSBSLocationService()
      return temp 
    elif source.lower() == "nyt":
      temp = NYTLocationService()
      return temp
    else:
      temp = JhuLocationService()
      return temp
