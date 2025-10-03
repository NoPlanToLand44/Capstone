from abc import ABC , abstractmethod
class AbstractNotificationManager(ABC):
    pass    

class NotificationManager(AbstractNotificationManager):
    
    def __init__ (self):
        self._history = []
    
    def send_terminal_notification(self, messages):
        if not messages: 
            print("no flights found ")
            return
        for message in messages:
            if not message:
                continue
            text = message.strip()
            self._history.append(text)
            print(text)
    
    
    # this will need to receive info from main and push data to the terminal or email , whatever is easier for me, dont want to do phone atm, 
    # too much red tape  so ill just use the terminal , when i run the program , it will let me know , based on the parameters ive chosen , 
    # what i have available in results.csv 
    # make a new dir , where u will store the reports and give them a name: search_results_exact_datetime to the minute
    pass