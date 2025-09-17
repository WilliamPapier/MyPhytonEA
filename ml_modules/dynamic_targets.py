# Dynamic Targets Module
import numpy as np

def calculate_dynamic_targets(setup, volatility=1.0):
    """Calculate dynamic TP/SL based on volatility"""
    base_tp = setup.get('entry', 0) * 1.02  # 2% TP
    base_sl = setup.get('entry', 0) * 0.98  # 2% SL
    
    # Adjust for volatility
    volatility_multiplier = max(0.5, min(2.0, volatility))
    
    return {
        'tp': base_tp * volatility_multiplier,
        'sl': base_sl / volatility_multiplier
    }