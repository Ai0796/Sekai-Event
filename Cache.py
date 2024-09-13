import json
import requests
import time
import os

class Cache:
    def __init__(self) -> None:
        self.cache = {}
        
        if not os.path.exists("cache"):
            os.makedirs("cache")
            
        if os.path.exists("cache/cache.json"):
            with open("cache/cache.json", "r") as f:
                self.cache = json.load(f)
        
        
    def load(self, key: str, url: str) -> None:
        
        unixTime = int(time.time())
        
        if key not in self.cache or self.cache[key] + 3600 < unixTime:

            r = requests.get(url)
            jsonData = r.json()
            
            with open(f"cache/{key}.json", "w") as f:
                json.dump(jsonData, f)
        
            self.cache[key] = unixTime
            
        else:
            with open(f"cache/{key}.json", "r") as f:
                jsonData = json.load(f)
                
        with open("cache/cache.json", "w") as f:
            json.dump(self.cache, f)
                
        return jsonData