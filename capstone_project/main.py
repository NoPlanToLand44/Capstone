from flight_data import FlightData
import json
from notification_manager import NotificationManager


class Main:
    
    def __init__(self):
        self.data = FlightData()
        self.data.get_all_flight_data()
        self.data.filter_flights(self.data.threashold)
        self.price_sorted = self.data.sortby("price")
        self.offers_for_user = []

    def get_data_for_notification(self, data):
        # gets 
        
        if data is not None:     
            for key, value in data.items(): 
                if len(value)>0 :
                    for i in value:
                        info = i['itineraries']
                        outbound_flight = info[0]
                        inbound_flight  = info[1]
                        offer_string = f"""
                        Avaliable flights for your desired dates: leaves from {outbound_flight['from']}, to : {outbound_flight['to']} at: {outbound_flight['departure']['at']}, 
                        returns to {outbound_flight['from']} at {inbound_flight['arrival']['at']} at a cost of: {i['price']} {self.data.parameters['currency']}
                        """
                        self.offers_for_user.append(offer_string)
        else: return None                       
        return self.offers_for_user
main = Main()
offers = main.get_data_for_notification(main.price_sorted)
notifier = NotificationManager()
notifier.send(offers)