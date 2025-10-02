import os
from pathlib import Path
import pandas as pd
from abc import ABC , abstractmethod



class Config(ABC):
    def __init__(self):
        pass
    @abstractmethod
    def read_config_excel(self):
        pass
    @abstractmethod
    def read_config_cli(self):
        pass
    @abstractmethod
    def validate_config(self):
        pass
    
    

class ConfigFetcher(Config):

    # This class is responsible for fetching info from the config sheet 
    # lets get all the info from our config file and assign it into easily accessed properties 
    def __init__(self):
        self.data = None
        self.parameters = None
        self.keys = None
    
    def read_config_excel(self):
        # getting the configuration from the file system 
        
        module_dir = Path(__file__).parent
        config_path = module_dir / "config_sheet"
        try:
            
            self.data = pd.read_excel(config_path/"config.csv", sheet_name='destinations')
            self.parameters = pd.read_excel(config_path/"config.csv", sheet_name='parameters')
            self.keys = pd.read_excel(config_path/"keys.csv", sheet_name="main")
           
            
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


    def read_config_cli(self):
        # TODO 
        pass
    
    def validate_config(self):
        # TODO 
        pass