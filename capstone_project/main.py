from flight_data import FlightData
from notification_manager import NotificationManager


class Main:
    
    def __init__(self):
        self.data = FlightData()
        self.offers_for_user = []

    def get_data_for_notification(self, data = None):
        # gets 
        try: 
            data = self.data.sortby("price")
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
        except ValueError:
            return print("value Error at get_data")
main = Main()
main.data.get_all_flight_data()
main.data.filter_flights()
offers = main.get_data_for_notification()
notifier = NotificationManager()
notifier.send_terminal_notification(offers)