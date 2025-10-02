import requests
import time
from datetime import datetime , date
from  config_fetcher import ConfigFetcher
from typing import Dict, Any
from abc import ABC , abstractmethod
import json


class AbstractSearch(ABC):
    
    # using the SOLID principles , we need to depend on abstractions 
    
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


        # we need to make sure we have an active token 
        # we validate the search parameters with RE 
config = ConfigFetcher()
config.read_config_excel()
# amadeus flight search engine API keys to be fetched from data_manager
try:
    API_PUBLIC = config.keys.loc[0,'value']
    API_SECRET = config.keys.loc[1,'value']
except Exception as e: 
    print(f"error in config : {e}")
    API_PUBLIC = None 
    API_SECRET = None

class AmadeusHttpClient(AbstractSearch):
    
    #This class is responsible for talking to the Flight Search API.
    # this needs to have all of the search parametrs with defaults that i choose with filters 
    
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
        # reload config if the first attempt failed
        if config.parameters is None or config.data is None:
            config.read_config_excel()
        if config.parameters is None or config.data is None:
            raise RuntimeError("Configuration sheets are missing or invalid. Check config_sheet/config.xlsx.")
        # gathering all the params 
        self.parameters = {i['parameter']: i['value'] for i in config.parameters.to_dict("records")}
        # setting the date to datetime objects in case we want to use them for analysis 
        self._format_date(self.parameters['departure_date'])
        self._format_date(self.parameters['return_date'])
        # getting the destinations 
        self.destinations = [
            code.strip().upper()
            for code in config.data['IATA Code'].dropna().astype(str)
            if code.strip()
        ]
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
                    originLocationCode : str  ,
                    destinationLocationCode : str ,
                    departureDate :datetime , 
                    maxPrice:int  ,
                    adults = 1,
                    returnDate: datetime | None = None ,
                    nonStop:bool = True,
                    currencyCode = "EUR", 
                    max_offers = 5
                     )->dict[list, Any]:
        # this makes the query to Amadeus and returns a normalized dict of the stuff we are interested in  
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
        self.meta = payload.get('meta',{})
        self.raw_data = payload.get('data',[])
        self.dictionaries = payload.get('dictionaries', {} )        
        if not self.raw_data:
            return []
        
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
        # we want to query a return flights so we check for no layover tickets two way 
        legs = []
        for idx, itin in enumerate(itineraries):
            first_seg = itin['segments'][0]
            last_seg = itin['segments'][-1]
            legs.append({
                'direction': "outbound" if idx == 0 else "return",
                "duration": itin['duration'],
                "from" : first_seg['departure']['iataCode'],
                "to": last_seg['arrival']['iataCode'],
                "departure": first_seg['departure'],
                "arrival": last_seg['arrival'],
                "carrier_code": first_seg['carrierCode'],
                "aircraft_code": first_seg['aircraft']['code'] if isinstance(first_seg.get('aircraft'), dict) else first_seg.get('aircraft'),
                "stops": max(0, len(itin.get('segments', [])) - 1),
          })
        return legs
    
    def _format_date(self, value):
        # takes in a string and returns a datetime or a datetime and retunrs a string 
        fmt = "%Y-%m-%d"
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            try:
                datetime.strptime(value, fmt)
            except ValueError as e:
                raise ValueError(f"Expected date formatted as {fmt}, got {value!r}") from e
            return value
        if hasattr(value, "to_pydatetime"):
            value = value.to_pydatetime()
        if isinstance(value, datetime):
            return value.strftime(fmt)
        if isinstance(value, date):
            return value.strftime(fmt)
        raise TypeError(f"Unsupported date value type: {type(value).__name__}")
    
# ------------------- testing


#obj = AmadeusHttpClient(API_PUBLIC,API_SECRET)
#print(obj.query_flight("MAD", "lon", datetime.strptime("2025-10-10", "%Y-%m-%d"), maxPrice=300, adults=1, returnDate=datetime.strptime("2025-10-15", "%Y-%m-%d"), nonStop=True))

