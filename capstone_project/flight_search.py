import requests
import time
from datetime import datetime 
from  config_fetcher import ConfigFetcher
from typing import Dict, Any

# this needs to have all of the search parametrs with defaults that i choose with filters 
        # we need to make sure we have an active token 
        # we validate the search parameters with RE 



try:
    API_PUBLIC = ConfigFetcher().keys.loc[0,'value']
    API_SECRET = ConfigFetcher().keys.loc[1,'value']
except Exception as e: 
    print(f"error in config : {e}")
    API_PUBLIC = None 
    API_SECRET = None
# amadeus flight search engine API keys to be fetched from data_manager
class FlightSearch:
    
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
    
    def authenticate(self):
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
            self.authenticate()
            
    def query_flight(self,
                    originLocationCode : str,
                    destinationLocationCode : str, 
                    departureDate :str, 
                    maxPrice:int = None,
                    adults = 1,
                    returnDate: str | None = None ,
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
        
        return response.json()
        
    def _format_date(self, date_str):
        
        date_formats = [
        "%Y-%m-%d",   # 2025-03-27
        "%d-%m-%Y",   # 27-03-2025
        "%d/%m/%Y",   # 27/03/2025
        "%m/%d/%Y",   # 03/27/2025
        "%d-%m-%y",   # 27-03-25
        "%m/%d/%y",   # 03/27/25
        "%B %d, %Y",  # March 27, 2025
        "%b %d, %Y",  # Mar 27, 2025
        "%d %B %Y",   # 27 March 2025
        "%d %b %Y",   # 27 Mar 2025
        ]
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return ValueError(f"date format not recognized")
        
        
    
# ------------------- testing

obj = FlightSearch(API_PUBLIC,API_SECRET)
print(obj.query_flight("MAD", "lon", "2025-09-29", maxPrice=300, adults=1, returnDate="2025-10-05", nonStop=True))

