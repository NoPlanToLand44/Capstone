import requests
import time
from datetime import datetime 
from  config_fetcher import ConfigFetcher
from typing import Dict, Any
from abc import ABC , abstractmethod
import json


class AbstractSearch(ABC):
    
    
    
    @abstractmethod
    def _ensure_authentication(self):
        pass
    @abstractmethod
    def _authenticate(self):
        pass
    @abstractmethod
    def query_flight(self,
                    originLocationCode ,
                    destinationLocationCode , 
                    departureDate, 
                    maxPrice,
                    adults ,
                    returnDate,
                    nonStop ,
                    currencyCode , 
                    max_offers):
        pass
    @abstractmethod
    def _get_flight_details(self, itineraries):
        pass
    @abstractmethod
    def _normalize_offer(self, offer):
        # we get from the response what we are interested in and structure it 
        pass

# this needs to have all of the search parametrs with defaults that i choose with filters 
        # we need to make sure we have an active token 
        # we validate the search parameters with RE 
config = ConfigFetcher()
config.read_config_excel()

try:
    API_PUBLIC = config.keys.loc[0,'value']
    API_SECRET = config.keys.loc[1,'value']
except Exception as e: 
    print(f"error in config : {e}")
    API_PUBLIC = None 
    API_SECRET = None
# amadeus flight search engine API keys to be fetched from data_manager
class AmadeusHttpClient(AbstractSearch):
    
    #This class is responsible for talking to the Flight Search API.
    
    AUTH_URL = "/v1/security/oauth2/token"
    SAERCH_URL = "/v2/shopping/flight-offers"
    PRICING_URL = "/v1/shopping/flight-offers/pricing"
    
    def __init__(self,
                api_public: str,
                api_secret: str,
                BASE_URL = "https://test.api.amadeus.com",
                timeout = 20,
                max_retries = 3, 
                ):
        self.api_public = api_public 
        self.api_secret = api_secret
        self.BASE_URL = BASE_URL
        self.timeout = timeout
        self.max_retries = max_retries
        self.access_token:str = None 
        self.access_token_expiry: int = None
        self.meta = None
        self.raw_data = None
        self.dictionaries = None
        self._last_results = None
        
    
    def _authenticate(self):
        # fetching auth token from amadeus
        token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        data = {
            "grant_type":"client_credentials",
            "client_id": self.api_public,
            "client_secret": self.api_secret
        }
        try: 
            response = requests.post(token_url, data=data, timeout=10)
            response.raise_for_status()
            token_info = response.json()
            self.access_token_expiry = time.time() + 1799
            self.access_token = token_info['access_token']
        except requests.exceptions.HTTPError as e: 
            print(f"some http error occured : {e}")    
            
    def _ensure_authentication(self) -> None:
        # make sure we always have a valid token to query
        now = time.time()
        if not self.access_token or now > self.access_token_expiry -100:
            self._authenticate()
            
    def query_flight(self,
                    originLocationCode : str,
                    destinationLocationCode : str, 
                    departureDate :datetime, 
                    maxPrice:int = None,
                    adults = 1,
                    returnDate: datetime | None = None ,
                    nonStop:bool = True,
                    currencyCode = "EUR", 
                    max_offers = 5
                     )->dict[list, Any]:
        self._ensure_authentication()
        params = {
            "originLocationCode":originLocationCode.upper(),
            "destinationLocationCode" : destinationLocationCode.upper(),
            "departureDate": self._format_date(departureDate),
            "adults": adults
        }
        
        if maxPrice is not None:
            params['maxPrice'] = maxPrice
        if returnDate is not None: 
            params['returnDate'] = self._format_date(returnDate)
        if nonStop is not None: 
            params['nonStop'] = str(nonStop).lower()
        if currencyCode is not None:
            params['currencyCode'] = currencyCode.upper()
        if max_offers is not None: 
            params['max'] = max_offers
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept":"application/json"
        }
        
        
        try: 
            response = requests.get(f"{self.BASE_URL}/{self.SAERCH_URL}", params = params, headers= headers, timeout=self.timeout)
        
        except Exception as e: 
            print(f"something failed at {e}")
        
        payload = response.json()
        self.meta = payload['meta']
        self.raw_data = payload['data']
        self.dictionaries = payload['dictionaries']        
        # fix return after the exp
        # return a normalized offer for use and further analysis
        # remove json.dumps!!
        return ([self._normalize_offer(offer) for offer in self.raw_data])
        
    def _normalize_offer(self, offer: dict ):
        # loop through the offer and get what we are interested in: 
        normalized_offer = {
            "id": offer['id'],
            "source": offer['source'],
            # abstracting away some of the complexity to a diferent function
            "itineraries": self._get_flight_details(offer['itineraries']),
            "price": offer['price']['total'],
            
        }
        
        return normalized_offer
    
    def _get_flight_details(self, itineraries: dict):
        for i in itineraries:
            
            details = {
                "duration": i['duration'],
                "departure": i['segments'][0]['departure'],
                "arrival": i['segments'][0]['arrival'],
                'carrier_code': i['segments'][0]['carrierCode'],
                'aircraft_code': i['segments'][0]['aircraft']
            }
        return details
    
    def _format_date(self, date):
        # fix strings, use internal datetime before sending to Amadeu
        fmt = "%Y-%m-%d"
        try:
            dt = date.strftime(fmt)
        except ValueError:
            print(f"something is wrong with the dates")
        return dt
    
# ------------------- testing


obj = AmadeusHttpClient(API_PUBLIC,API_SECRET)
print(obj.query_flight("MAD", "lon", datetime.strptime("2025-10-10", "%Y-%m-%d"), maxPrice=300, adults=1, returnDate=datetime.strptime("2025-10-15", "%Y-%m-%d"), nonStop=True))

