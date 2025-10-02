from flight_search import AmadeusHttpClient, API_PUBLIC, API_SECRET
from abc import ABC , abstractmethod
from datetime import datetime
from  config_fetcher import ConfigFetcher
import json


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
        self.http_client = AmadeusHttpClient(API_PUBLIC,API_SECRET)
        self.destinations = self.http_client.destinations
        self.parameters = self.http_client.parameters
        self.all_offers = {}
        
        # putting all data i am interested in, in a list 
    
    def get_all_flight_data(self):
        dep_code = self.parameters['departure_city_code']     
        dep_date = self.http_client._format_date(self.parameters['departure_date'])           
        ret_date = self.http_client._format_date(self.parameters['return_date'])             
        max_price = self.parameters['max_price'] 
        currency_code = self.parameters['currency']  
        for city in self.destinations: 
            try:
                offers = self.http_client.query_flight(originLocationCode=dep_code ,
                                 destinationLocationCode=city, 
                                 departureDate=dep_date, 
                                 currencyCode= currency_code, 
                                 maxPrice=max_price, 
                                 adults=1, 
                                 returnDate=ret_date, 
                                 nonStop=True)
                self.all_offers[city] = offers
            except Exception as e:
                self.all_offers[city] = []
                print(e)
        return self.all_offers
            


# ------ testing: 
data = FlightData()
data.get_all_flight_data()
print(json.dumps(data.all_offers))
# TODO i am getting a response from amadeus but fucking something up with the processing 