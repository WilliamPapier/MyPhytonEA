"""
Enhanced Dash dashboard for EA/Scanner system with comprehensive controls,
goal tracking, and real-time configuration management.
"""
import dash
from dash import html, dcc, dash_table, Output, Input, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import numpy as np

# Initialize Dash app
external_stylesheets = [dbc.themes.DARKLY, 'https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

# Instruments list
INSTRUMENTS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "NZDUSD", "USDCHF", 
    "USDCAD", "XAUUSD", "US30", "NAS100"
]

def make_request(endpoint, method="GET", data=None):
    """Make request to backend with error handling"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Request error: {e}")
        return None

# Layout components
def create_control_panel():
    """Create the control panel for threshold and risk settings"""
    return dbc.Card([
        dbc.CardHeader("Control Panel"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Probability Threshold"),
                    dcc.Slider(
                        id="probability-threshold-slider",
                        min=0.0, max=1.0, step=0.05, value=0.75,
                        marks={i/10: f"{i/10:.1f}" for i in range(0, 11, 2)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                ], width=6),
                dbc.Col([
                    html.Label("Risk per Trade (%)"),
                    dcc.Slider(
                        id="risk-per-trade-slider", 
                        min=0.5, max=5.0, step=0.25, value=2.0,
                        marks={i: f"{i}%" for i in range(1, 6)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                ], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Max Simultaneous Trades"),
                    dcc.Slider(
                        id="max-trades-slider",
                        min=1, max=10, step=1, value=3,
                        marks={i: str(i) for i in range(1, 11)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                ], width=6),
                dbc.Col([
                    html.Label("Max Daily Risk (%)"),
                    dcc.Slider(
                        id="max-daily-risk-slider",
                        min=2, max=15, step=1, value=6,
                        marks={i: f"{i}%" for i in range(2, 16, 2)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                ], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Checklist(
                        id="feature-toggles",
                        options=[
                            {"label": "Dynamic Lotsize", "value": "dynamic_lotsize"},
                            {"label": "Pyramiding", "value": "pyramiding"},
                            {"label": "Trailing Stop", "value": "trailing_stop"},
                            {"label": "Optimal TP", "value": "optimal_tp"}
                        ],
                        value=["dynamic_lotsize", "pyramiding", "trailing_stop", "optimal_tp"],
                        inline=True
                    ),
                ], width=12),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Update Settings", id="update-settings-btn", 
                              color="primary", className="mt-2"),
                    html.Div(id="settings-status", className="mt-2")
                ], width=12),
            ])
        ])
    ], className="mb-4")

def create_overview_cards():
    """Create overview cards for key metrics"""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("0", id="account-balance", className="text-success"),
                    html.P("Account Balance", className="card-text"),
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("0", id="active-trades-count", className="text-info"),
                    html.P("Active Trades", className="card-text"),
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("0%", id="win-rate", className="text-warning"),
                    html.P("Win Rate", className="card-text"),
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("0%", id="daily-progress", className="text-primary"),
                    html.P("Daily Goal Progress", className="card-text"),
                ])
            ])
        ], width=3),
    ], className="mb-4")

def create_goal_tracking():
    """Create goal tracking section"""
    return dbc.Card([
        dbc.CardHeader("Goal Tracking"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H5("Daily Goal"),
                    dbc.Progress(id="daily-goal-progress", value=0, className="mb-2"),
                    html.Div(id="daily-goal-text")
                ], width=4),
                dbc.Col([
                    html.H5("Weekly Goal"),
                    dbc.Progress(id="weekly-goal-progress", value=0, className="mb-2"),
                    html.Div(id="weekly-goal-text")
                ], width=4),
                dbc.Col([
                    html.H5("Monthly Goal"),
                    dbc.Progress(id="monthly-goal-progress", value=0, className="mb-2"),
                    html.Div(id="monthly-goal-text")
                ], width=4),
            ])
        ])
    ], className="mb-4")

def create_setups_table():
    """Create setups table with filtering"""
    return dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col("Active Setups", width=6),
                dbc.Col([
                    dcc.Dropdown(
                        id="setup-filter",
                        options=[
                            {"label": "All Setups", "value": "all"},
                            {"label": "Above Threshold", "value": "above_threshold"},
                            {"label": "Strong Signals", "value": "strong"},
                            {"label": "Medium Signals", "value": "medium"}
                        ],
                        value="above_threshold",
                        clearable=False
                    )
                ], width=6)
            ])
        ]),
        dbc.CardBody([
            dash_table.DataTable(
                id="setups-table",
                columns=[
                    {"name": "Symbol", "id": "symbol"},
                    {"name": "Pattern", "id": "pattern"},
                    {"name": "Probability", "id": "probability", "type": "numeric", "format": {"specifier": ".2%"}},
                    {"name": "Signal Strength", "id": "signal_strength"},
                    {"name": "Recommendation", "id": "recommendation"},
                    {"name": "Timestamp", "id": "timestamp"}
                ],
                style_cell={'textAlign': 'left', 'backgroundColor': '#2b2b2b', 'color': 'white'},
                style_header={'backgroundColor': '#404040', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{recommendation} = trade'},
                        'backgroundColor': '#155724',
                        'color': 'white',
                    },
                    {
                        'if': {'filter_query': '{recommendation} = consider'},
                        'backgroundColor': '#856404',
                        'color': 'white',
                    }
                ],
                page_size=10,
                sort_action="native"
            )
        ])
    ], className="mb-4")

def create_trades_table():
    """Create active trades table"""
    return dbc.Card([
        dbc.CardHeader("Active Trades"),
        dbc.CardBody([
            dash_table.DataTable(
                id="trades-table",
                columns=[
                    {"name": "Symbol", "id": "symbol"},
                    {"name": "Direction", "id": "direction"},
                    {"name": "Entry", "id": "entry_price", "type": "numeric"},
                    {"name": "Size", "id": "position_size", "type": "numeric"},
                    {"name": "SL", "id": "stop_loss", "type": "numeric"},
                    {"name": "TP", "id": "take_profit", "type": "numeric"},
                    {"name": "P&L", "id": "profit_loss", "type": "numeric"},
                    {"name": "Time", "id": "timestamp"}
                ],
                style_cell={'textAlign': 'left', 'backgroundColor': '#2b2b2b', 'color': 'white'},
                style_header={'backgroundColor': '#404040', 'fontWeight': 'bold'},
                page_size=10
            )
        ])
    ], className="mb-4")

def create_performance_charts():
    """Create performance visualization charts"""
    return dbc.Card([
        dbc.CardHeader("Performance Analytics"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="equity-curve")
                ], width=6),
                dbc.Col([
                    dcc.Graph(id="pattern-performance")
                ], width=6),
            ])
        ])
    ], className="mb-4")

# Main layout
app.layout = html.Div([
    dcc.Store(id="config-store"),
    dcc.Interval(id="interval", interval=5*1000, n_intervals=0),  # Update every 5 seconds
    
    html.Div(className="container-fluid", children=[
        html.H1("EA/Scanner Control Dashboard", className="text-center mb-4"),
        
        create_control_panel(),
        create_overview_cards(),
        create_goal_tracking(),
        create_setups_table(),
        create_trades_table(),
        create_performance_charts(),
        
        # Status and notifications
        dbc.Card([
            dbc.CardHeader("System Status"),
            dbc.CardBody([
                html.Div(id="system-status"),
                html.Div(id="notifications-area")
            ])
        ])
    ])
])

# Callbacks
@app.callback(
    [Output("config-store", "data"),
     Output("probability-threshold-slider", "value"),
     Output("risk-per-trade-slider", "value"),
     Output("max-trades-slider", "value"),
     Output("max-daily-risk-slider", "value"),
     Output("feature-toggles", "value")],
    [Input("interval", "n_intervals")]
)
def load_config(n):
    """Load configuration from backend"""
    config = make_request("/config")
    if config:
        feature_values = []
        if config.get("dynamic_lotsize_enabled", True):
            feature_values.append("dynamic_lotsize")
        if config.get("pyramiding_enabled", True):
            feature_values.append("pyramiding")
        if config.get("trailing_stop_enabled", True):
            feature_values.append("trailing_stop")
        if config.get("optimal_tp_enabled", True):
            feature_values.append("optimal_tp")
        
        return (
            config,
            config.get("probability_threshold", 0.75),
            config.get("risk_per_trade_percent", 2.0),
            config.get("max_simultaneous_trades", 3),
            config.get("max_daily_risk_percent", 6.0),
            feature_values
        )
    
    return {}, 0.75, 2.0, 3, 6.0, ["dynamic_lotsize", "pyramiding", "trailing_stop", "optimal_tp"]

@app.callback(
    Output("settings-status", "children"),
    [Input("update-settings-btn", "n_clicks")],
    [State("probability-threshold-slider", "value"),
     State("risk-per-trade-slider", "value"),
     State("max-trades-slider", "value"),
     State("max-daily-risk-slider", "value"),
     State("feature-toggles", "value")]
)
def update_settings(n_clicks, threshold, risk_percent, max_trades, max_daily_risk, features):
    """Update settings in backend"""
    if n_clicks is None:
        return ""
    
    updates = {
        "probability_threshold": threshold,
        "risk_per_trade_percent": risk_percent,
        "max_simultaneous_trades": max_trades,
        "max_daily_risk_percent": max_daily_risk,
        "dynamic_lotsize_enabled": "dynamic_lotsize" in features,
        "pyramiding_enabled": "pyramiding" in features,
        "trailing_stop_enabled": "trailing_stop" in features,
        "optimal_tp_enabled": "optimal_tp" in features
    }
    
    result = make_request("/config/bulk", "POST", updates)
    if result:
        return dbc.Alert("Settings updated successfully!", color="success", dismissable=True)
    else:
        return dbc.Alert("Failed to update settings", color="danger", dismissable=True)

@app.callback(
    [Output("account-balance", "children"),
     Output("active-trades-count", "children"),
     Output("win-rate", "children"),
     Output("daily-progress", "children")],
    [Input("interval", "n_intervals")]
)
def update_overview(n):
    """Update overview cards"""
    # Get risk summary
    risk_data = make_request("/risk/summary")
    performance_data = make_request("/performance/summary")
    goals_data = make_request("/performance/goals")
    
    balance = "$0"
    active_count = "0"
    win_rate = "0%"
    daily_progress = "0%"
    
    if risk_data:
        balance = f"${risk_data.get('account_balance', 0):,.2f}"
        active_count = str(risk_data.get('active_trades', 0))
    
    if performance_data:
        trading_perf = performance_data.get('trading_performance', {})
        win_rate = f"{trading_perf.get('win_rate', 0)*100:.1f}%"
    
    if goals_data:
        daily_data = goals_data.get('daily', {})
        daily_progress = f"{daily_data.get('progress_percent', 0):.1f}%"
    
    return balance, active_count, win_rate, daily_progress

@app.callback(
    [Output("daily-goal-progress", "value"),
     Output("weekly-goal-progress", "value"),
     Output("monthly-goal-progress", "value"),
     Output("daily-goal-text", "children"),
     Output("weekly-goal-text", "children"),
     Output("monthly-goal-text", "children")],
    [Input("interval", "n_intervals")]
)
def update_goals(n):
    """Update goal tracking"""
    goals_data = make_request("/performance/goals")
    
    if goals_data:
        daily = goals_data.get('daily', {})
        weekly = goals_data.get('weekly', {})
        monthly = goals_data.get('monthly', {})
        
        return (
            min(daily.get('progress_percent', 0), 100),
            min(weekly.get('progress_percent', 0), 100),
            min(monthly.get('progress_percent', 0), 100),
            f"${daily.get('actual', 0):.2f} / ${daily.get('goal', 0):.2f}",
            f"${weekly.get('actual', 0):.2f} / ${weekly.get('goal', 0):.2f}",
            f"${monthly.get('actual', 0):.2f} / ${monthly.get('goal', 0):.2f}"
        )
    
    return 0, 0, 0, "$0 / $0", "$0 / $0", "$0 / $0"

@app.callback(
    Output("setups-table", "data"),
    [Input("interval", "n_intervals"),
     Input("setup-filter", "value")]
)
def update_setups_table(n, filter_value):
    """Update setups table"""
    setups_data = make_request("/setups")
    
    if setups_data and setups_data.get('setups'):
        setups = setups_data['setups']
        
        # Apply filters
        if filter_value == "above_threshold":
            threshold = setups_data.get('threshold', 0.75)
            setups = [s for s in setups if s.get('probability', 0) >= threshold]
        elif filter_value == "strong":
            setups = [s for s in setups if s.get('signal_strength') == 'strong']
        elif filter_value == "medium":
            setups = [s for s in setups if s.get('signal_strength') == 'medium']
        
        # Format data for table
        table_data = []
        for setup in setups[-20:]:  # Last 20 setups
            table_data.append({
                'symbol': setup.get('symbol', ''),
                'pattern': setup.get('pattern', ''),
                'probability': setup.get('probability', 0),
                'signal_strength': setup.get('signal_strength', ''),
                'recommendation': setup.get('recommendation', ''),
                'timestamp': setup.get('timestamp', '')[:16] if setup.get('timestamp') else ''
            })
        
        return table_data
    
    return []

@app.callback(
    Output("trades-table", "data"),
    [Input("interval", "n_intervals")]
)
def update_trades_table(n):
    """Update active trades table"""
    trades_data = make_request("/trades")
    
    if trades_data and trades_data.get('active_trades'):
        trades = trades_data['active_trades']
        
        table_data = []
        for trade in trades:
            table_data.append({
                'symbol': trade.get('symbol', ''),
                'direction': trade.get('direction', ''),
                'entry_price': trade.get('entry_price', 0),
                'position_size': trade.get('position_size', 0),
                'stop_loss': trade.get('stop_loss', 0),
                'take_profit': trade.get('take_profit', 0),
                'profit_loss': trade.get('profit_loss', 0),
                'timestamp': trade.get('timestamp', '')[:16] if trade.get('timestamp') else ''
            })
        
        return table_data
    
    return []

@app.callback(
    [Output("equity-curve", "figure"),
     Output("pattern-performance", "figure")],
    [Input("interval", "n_intervals")]
)
def update_charts(n):
    """Update performance charts"""
    performance_data = make_request("/performance/summary")
    
    # Default empty charts
    equity_fig = go.Figure()
    equity_fig.add_trace(go.Scatter(x=[datetime.now()], y=[10000], name="Equity"))
    equity_fig.update_layout(title="Equity Curve", template="plotly_dark")
    
    pattern_fig = go.Figure()
    pattern_fig.add_trace(go.Bar(x=["No Data"], y=[0], name="Win Rate"))
    pattern_fig.update_layout(title="Pattern Performance", template="plotly_dark")
    
    if performance_data:
        scoring_perf = performance_data.get('scoring_performance', {})
        best_patterns = scoring_perf.get('best_patterns', [])
        
        if best_patterns:
            patterns = [p[0] for p in best_patterns]
            win_rates = [p[1] * 100 for p in best_patterns]
            
            pattern_fig = go.Figure()
            pattern_fig.add_trace(go.Bar(x=patterns, y=win_rates, name="Win Rate %"))
            pattern_fig.update_layout(title="Best Pattern Performance", template="plotly_dark")
    
    return equity_fig, pattern_fig

@app.callback(
    Output("system-status", "children"),
    [Input("interval", "n_intervals")]
)
def update_system_status(n):
    """Update system status"""
    health_data = make_request("/health")
    
    if health_data:
        status_color = "success" if health_data.get('status') == 'healthy' else "danger"
        return dbc.Alert([
            html.H5("System Status: " + health_data.get('status', 'unknown').title()),
            html.P(f"Active Setups: {health_data.get('active_setups', 0)}"),
            html.P(f"Active Trades: {health_data.get('active_trades', 0)}"),
            html.P(f"Last Update: {health_data.get('timestamp', '')}"),
        ], color=status_color)
    
    return dbc.Alert("Backend connection failed", color="danger")

if __name__ == "__main__":
    app.run(debug=True, port=8050)