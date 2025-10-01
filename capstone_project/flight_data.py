from flight_search import AmadeusHttpClient, API_PUBLIC, API_SECRET
from abc import ABC , abstractmethod
from datetime import datetime
from  config_fetcher import ConfigFetcher


class AbstractDataStructure(ABC):
    @abstractmethod
    def get_all_flight_data(self, *args, **kwargs):
        pass
    
    def groupby(self, groupby_parameter):
        pass
    
    
    

class FlightData(AbstractDataStructure):
    #This class is responsible for structuring the flight data.
    # it will need to get the data from the flight_search class and stcture it in useful ways 
    # fetching the flights from the flight search, group them by cities, time and cost 
    def __init__(self, ):
        http_client = AmadeusHttpClient(API_PUBLIC,API_SECRET)
        # putting all data i am interested in, in a list 
        http_client.query_flight("MAD", "lon", datetime.strptime("2025-10-10", "%Y-%m-%d"), maxPrice=300, adults=1, returnDate=datetime.strptime("2025-10-15", "%Y-%m-%d"), nonStop=True))
       


