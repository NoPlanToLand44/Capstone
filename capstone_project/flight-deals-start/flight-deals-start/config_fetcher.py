import os
from pathlib import Path
import pandas as pd
class ConfigFetcher:

    # This class is responsible for fetching info from the config sheet 
    # lets get all the info from our config file and assign it into easily accessed properties 
    def __init__(self):
        config_path = Path("config_sheet")
        try:
            self.data = pd.read_excel(config_path/"config.csv", sheet_name='destinations') 
            self.parameters = pd.read_excel(config_path/"config.csv", sheet_name='parameters')
            self.keys = pd.read_excel(config_path/"keys.csv", sheet_name="main") 
            print(self.keys)
            # make a pandas  table for the data
            # make methods for reading the doc 
            
        except FileNotFoundError:
            print(f"file not found at {config_path}")
            print(f'current working dir: {os.getcwd()}')
            self.data = None
        except ValueError as e: 
            print(f"sheet destinations not found in file {e}")
            self.data = None
        except Exception as e:
            print(f"another exception: {e}")
            self.data = None
