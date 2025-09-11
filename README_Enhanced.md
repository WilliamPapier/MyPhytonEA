# Enhanced EA/Scanner Trading System

A comprehensive, modular trading system with real-time configuration management, stats-based scoring, and advanced risk management features.

## 🚀 Features

### Core Features Implemented

✅ **Global Probability Threshold System**
- Single threshold adjustable from dashboard
- Real-time updates to all modules via FastAPI
- Immediate filtering of setups and trades

✅ **Stats-Based Scoring System**
- Classic win rate logic (Pattern X in context Y = X% probability)
- Modular design for future ML integration
- Pattern recognition with context awareness

✅ **Enhanced Dashboard (Dash)**
- Real-time setup/trade filtering by probability threshold
- Daily, weekly, monthly goal tracking with progress bars
- Risk management controls (lotsize, risk %, max trades)
- Live configuration updates every 5 seconds

✅ **Dynamic Risk Management**
- Auto-scaling lotsize based on equity growth
- Fixed percentage risk per trade
- Configurable maximum simultaneous trades
- Daily risk exposure monitoring

✅ **Pyramiding/Multiple Entries**
- Support for multiple trades on same instrument
- Independent management of each trade
- Configurable maximum trades per setup

✅ **Advanced Trailing Stops**
- Multiple methods: Fixed pips, ATR-based, Structure-based
- Never closes trades prematurely if trend continues
- Intelligent profit protection

✅ **Optimal Take Profit Analysis**
- Historical data analysis for optimal TP levels
- Maximize reward while maintaining high win rates
- Dynamic TP adjustment based on market conditions

✅ **Extended Trade Management**
- Hold trades for hours if structure remains valid
- Exit only on structure break, SL, or TP
- Smart trend continuation detection

## 🏗️ Architecture

### System Components

```
Enhanced EA/Scanner System
├── FastAPI Backend (Port 8000)
│   ├── Configuration Management
│   ├── Setup Scoring & Filtering
│   ├── Trade Management
│   ├── Risk Monitoring
│   └── Performance Analytics
├── Dash Dashboard (Port 8050)
│   ├── Control Panel
│   ├── Goal Tracking
│   ├── Setup/Trade Tables
│   ├── Performance Charts
│   └── System Status
├── Core Modules
│   ├── config.py - Global configuration
│   ├── scoring.py - Stats-based scoring
│   ├── trailing_stops.py - Stop management
│   └── optimal_tp.py - TP optimization
├── Scanner System
│   ├── enhanced_scanner.py - Main scanner
│   └── Pattern detection & submission
└── Data Exchange
    ├── CSV files for EA integration
    ├── JSON configuration files
    └── Real-time API communication
```

### Key Files

| File | Purpose |
|------|---------|
| `config.py` | Thread-safe global configuration management |
| `scoring.py` | Stats-based setup scoring with pattern recognition |
| `enhanced_backend.py` | FastAPI server with real-time controls |
| `enhanced_dashboard.py` | Comprehensive Dash dashboard |
| `trailing_stops.py` | Multi-method trailing stop management |
| `optimal_tp.py` | Historical TP analysis and optimization |
| `enhanced_scanner.py` | Pattern detection and setup submission |
| `test_system.py` | Comprehensive system testing |

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements_new.txt
```

### Running the System

1. **Start the Backend**
```bash
python enhanced_backend.py
```
Backend will be available at `http://localhost:8000`

2. **Start the Dashboard**
```bash
python enhanced_dashboard.py
```
Dashboard will be available at `http://localhost:8050`

3. **Run the Scanner** (Optional)
```bash
python enhanced_scanner.py
```

4. **Test the System**
```bash
python test_system.py
python test_scanner.py
```

## 📊 Dashboard Features

### Control Panel
- **Probability Threshold**: 0.0 - 1.0 (real-time updates)
- **Risk per Trade**: 0.5% - 5.0% 
- **Max Simultaneous Trades**: 1 - 10
- **Max Daily Risk**: 2% - 15%
- **Feature Toggles**: Dynamic Lotsize, Pyramiding, Trailing Stops, Optimal TP

### Overview Cards
- **Account Balance**: Current equity
- **Active Trades**: Number of open positions  
- **Win Rate**: Historical success rate
- **Daily Goal Progress**: Progress towards daily target

### Goal Tracking
- **Daily Goal**: 2% of account balance
- **Weekly Goal**: 10% of account balance  
- **Monthly Goal**: 30% of account balance
- Real-time progress bars and P&L tracking

### Active Setups Table
- Pattern identification and probability scores
- Signal strength and recommendations
- Filterable by threshold and signal strength
- Real-time updates with new setups

### Performance Analytics
- Equity curve visualization
- Pattern performance charts
- Best/worst performing patterns
- Historical win rate analysis

## 🔧 Configuration

### Global Settings (config.json)
```json
{
  "probability_threshold": 0.75,
  "risk_per_trade_percent": 2.0,
  "max_simultaneous_trades": 3,
  "dynamic_lotsize_enabled": true,
  "pyramiding_enabled": true,
  "trailing_stop_enabled": true,
  "trailing_stop_method": "atr",
  "optimal_tp_enabled": true,
  "hold_time_hours": 8,
  "account_balance": 10000.0
}
```

### Pattern Scoring
The system uses classic statistics to score patterns:
- **Pattern Recognition**: Liquidity sweeps, order blocks, pin bars
- **Context Analysis**: Market session, volatility, trend direction
- **Win Rate Calculation**: Historical performance in similar contexts
- **Confidence Scoring**: Based on available data samples

## 📈 API Endpoints

### Configuration
- `GET /config` - Get all configuration
- `POST /config` - Update configuration value
- `GET /threshold` - Get probability threshold
- `POST /threshold` - Set probability threshold

### Setup Management
- `POST /scanner/submit` - Submit setup for scoring
- `GET /setups` - Get active setups
- `GET /setups/{id}` - Get specific setup

### Trade Management  
- `POST /trades/open` - Open new trade
- `GET /trades` - Get all trades
- `POST /trades/{id}/close` - Close trade

### Analytics
- `GET /performance/summary` - Performance statistics
- `GET /performance/goals` - Goal tracking data
- `GET /risk/summary` - Risk exposure summary

## 🧪 Testing

Run comprehensive tests:
```bash
python test_system.py
```

Test scanner functionality:
```bash
python test_scanner.py
```

## 📁 Data Exchange

### CSV Files for EA Integration
- `active_setups.csv` - Setups above threshold
- `active_trades.csv` - Open trades for management
- `setup_history.json` - Historical pattern performance
- `tp_analysis.json` - Optimal TP analysis data

## 🔒 Risk Management

### Position Sizing
```python
position_size = (account_balance * risk_percent) / (stop_loss_pips * pip_value)
```

### Risk Limits
- Maximum daily risk exposure
- Maximum simultaneous trades
- Dynamic lotsize scaling with equity growth
- Individual trade risk percentage

### Trailing Stops
- **ATR Method**: `new_stop = price ± (ATR × multiplier)`
- **Fixed Method**: `new_stop = price ± fixed_pips`  
- **Structure Method**: Based on swing highs/lows

## 🎯 Goal Tracking

### Calculation Logic
```python
daily_goal = account_balance * 0.02    # 2%
weekly_goal = account_balance * 0.10   # 10%  
monthly_goal = account_balance * 0.30  # 30%
```

### Progress Tracking
- Real-time P&L calculation
- Progress bars with percentage completion
- Color-coded indicators (green/amber/red)

## 🔮 Future Enhancements

The modular design allows for easy integration of:
- Machine Learning models for enhanced scoring
- Additional pattern recognition algorithms
- Advanced market structure analysis
- News sentiment integration
- Multi-timeframe correlation analysis

## 📝 Requirements

- Python 3.8+
- FastAPI for backend API
- Dash for dashboard interface
- NumPy/Pandas for calculations
- Requests for API communication
- Thread-safe configuration management

## ⚠️ Important Notes

- System designed for 6GB RAM laptops (efficient and lightweight)
- All modules communicate via FastAPI for real-time updates
- CSV files provide EA integration without complex APIs
- Configuration changes are immediately propagated to all components
- Built-in safety limits prevent excessive risk exposure

## 🤝 Contributing

The system is designed to be modular and extensible. Key extension points:
- `scoring.py` - Add new pattern recognition algorithms
- `optimal_tp.py` - Enhance TP optimization logic
- `trailing_stops.py` - Add new trailing stop methods
- `enhanced_dashboard.py` - Add new visualization components