from flight_search import AmadeusHttpClient, API_PUBLIC, API_SECRET
from abc import ABC , abstractmethod
from datetime import datetime
from  config_fetcher import ConfigFetcher
import json
import pandas as pd 


    

class FlightData():
    #This class is responsible for structuring the flight data.
    # it will need to get the data from the flight_search class and stcture it in useful ways 
    # fetching the flights from the flight search, group them by cities, time and cost 
    def __init__(self, ):
        self.http_client = AmadeusHttpClient(API_PUBLIC,API_SECRET)
        self.destinations = self.http_client.destinations
        self.parameters = self.http_client.parameters
        self.threashold = self.parameters['max_price']
        self.all_offers = {}
        self.all_offers_sorted = {}
        self.all_offers_filtered = {}
        
        
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
            
    def sortby(self, sort_parameter="price"):
        def key_fn(offer):
            try:
                return float(offer.get(sort_parameter))
            except (TypeError, ValueError):
                return float("inf")
        return {
            city: sorted(offers, key=key_fn)
            for city, offers in self.all_offers.items()
        }

    def filter_flights(self, filter_threashold=None):
        try:
            threshold = float(filter_threashold if filter_threashold is not None else self.threashold)
        except (TypeError, ValueError):
            raise ValueError("filter_threashold must be a number.")
        filtered = {}
        for city, offers in self.all_offers.items():
            filtered_offers = []
            for offer in offers:
                try:
                    price = float(offer.get("price"))
                except (TypeError, ValueError):
                    continue
                if price <= threshold:
                    filtered_offers.append(offer)
            if filtered_offers:
                filtered[city] = filtered_offers
        self.all_offers_filtered = filtered
        return self.all_offers_filtered