# Setup Storage Module
import json
import os
from datetime import datetime

class SetupStorage:
    def __init__(self, storage_path="./data/setups.json"):
        self.storage_path = storage_path
        self.setups = []
        
    def store_setup(self, setup):
        """Store a trading setup"""
        setup['timestamp'] = datetime.utcnow().isoformat()
        self.setups.append(setup)
        
    def get_setups(self, limit=100):
        """Get recent setups"""
        return self.setups[-limit:]