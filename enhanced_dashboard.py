"""
Enhanced Dashboard integrating all advanced trading systems

Features:
- Prop firm status monitoring
- Resource monitoring tab
- Advanced notifications
- Backtest results display
- Risk management controls
"""

import dash
from dash import html, dcc, Output, Input, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Initialize Dash app
external_stylesheets = [dbc.themes.DARKLY]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Enhanced layout with new tabs
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🚀 MyPhytonEA Trading System v2.0", 
                   className="text-center mb-4",
                   style={"color": "#00e6e6"})
        ])
    ]),
    
    # Status indicators row
    dbc.Row([
        dbc.Col([
            dbc.Badge("Prop Firm Mode", color="warning", id="prop-firm-badge", className="me-2"),
            dbc.Badge("System Health", color="success", id="health-badge", className="me-2"),
            dbc.Badge("Emergency Stop", color="danger", id="emergency-badge", className="me-2", style={"display": "none"}),
        ], width=12)
    ], className="mb-3"),
    
    # Main tabs
    dbc.Tabs([
        # Trading Dashboard Tab
        dbc.Tab(label="Trading Dashboard", tab_id="trading", children=[
            dcc.Interval(id="trading-interval", interval=5*1000, n_intervals=0),
            
            # Trading metrics cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Account Balance"),
                        dbc.CardBody(html.H3("R 0", id="balance", className="text-success")),
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Open Trades"),
                        dbc.CardBody(html.H3("0", id="open-trades", className="text-info")),
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Win Rate"),
                        dbc.CardBody(html.H3("0%", id="win-rate", className="text-warning")),
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Daily P&L"),
                        dbc.CardBody(html.H3("R 0", id="daily-pnl", className="text-primary")),
                    ])
                ], width=3),
            ], className="mb-4"),
            
            # Charts row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Equity Curve"),
                        dbc.CardBody(dcc.Graph(id="equity-chart"))
                    ])
                ], width=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Recent Trades"),
                        dbc.CardBody(html.Div(id="recent-trades"))
                    ])
                ], width=4),
            ]),
        ]),
        
        # Prop Firm Tab
        dbc.Tab(label="Prop Firm Control", tab_id="prop-firm", children=[
            dcc.Interval(id="prop-firm-interval", interval=10*1000, n_intervals=0),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Prop Firm Status"),
                        dbc.CardBody([
                            html.Div(id="prop-firm-status"),
                            html.Hr(),
                            dbc.Button("Detect Prop Firm", id="detect-btn", color="primary", className="me-2"),
                            dbc.Button("Emergency Stop", id="emergency-stop-btn", color="danger"),
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Daily Limits"),
                        dbc.CardBody([
                            html.Div(id="daily-limits")
                        ])
                    ])
                ], width=6),
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Prop Firm Rules"),
                        dbc.CardBody([
                            html.Div(id="prop-firm-rules")
                        ])
                    ])
                ])
            ])
        ]),
        
        # Resource Monitoring Tab
        dbc.Tab(label="System Monitor", tab_id="resources", children=[
            dcc.Interval(id="resource-interval", interval=15*1000, n_intervals=0),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("CPU Usage"),
                        dbc.CardBody([
                            dcc.Graph(id="cpu-chart")
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Memory Usage"),
                        dbc.CardBody([
                            dcc.Graph(id="memory-chart")
                        ])
                    ])
                ], width=6),
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("System Health"),
                        dbc.CardBody([
                            html.Div(id="system-health")
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Notifications"),
                        dbc.CardBody([
                            html.Div(id="notifications-list")
                        ])
                    ])
                ], width=6),
            ])
        ]),
        
        # Backtest Tab
        dbc.Tab(label="Backtest", tab_id="backtest", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Backtest Controls"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Start Date"),
                                    dcc.DatePickerSingle(
                                        id="backtest-start-date",
                                        date=(datetime.now() - timedelta(days=30)).date()
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("End Date"),
                                    dcc.DatePickerSingle(
                                        id="backtest-end-date",
                                        date=datetime.now().date()
                                    )
                                ], width=6),
                            ]),
                            html.Hr(),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Initial Balance"),
                                    dbc.Input(id="initial-balance", type="number", value=10000)
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Strategy"),
                                    dcc.Dropdown(
                                        id="strategy-dropdown",
                                        options=[
                                            {"label": "Moving Average Crossover", "value": "ma_crossover"},
                                            {"label": "RSI Strategy", "value": "rsi"},
                                            {"label": "Custom Strategy", "value": "custom"}
                                        ],
                                        value="ma_crossover"
                                    )
                                ], width=6),
                            ]),
                            html.Hr(),
                            dbc.Button("Run Backtest", id="run-backtest-btn", color="success", className="w-100")
                        ])
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Backtest Results"),
                        dbc.CardBody([
                            html.Div(id="backtest-results")
                        ])
                    ])
                ], width=8),
            ])
        ])
    ], id="main-tabs", active_tab="trading")
], fluid=True)

# Callback for trading dashboard updates
@app.callback(
    [Output("balance", "children"),
     Output("open-trades", "children"),
     Output("win-rate", "children"),
     Output("daily-pnl", "children"),
     Output("equity-chart", "figure"),
     Output("recent-trades", "children")],
    [Input("trading-interval", "n_intervals")]
)
def update_trading_dashboard(n):
    try:
        # This would connect to your enhanced server
        # For demo, using mock data
        
        # Mock trading data
        balance = f"R {10000 + n * 100:,.2f}"
        open_trades = str(max(0, 3 - (n % 5)))
        win_rate = f"{min(100, 65 + (n % 20))}%"
        daily_pnl = f"R {(n % 10) * 50 - 200:,.2f}"
        
        # Mock equity curve
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        equity = 10000 + np.cumsum(np.random.randn(100) * 50)
        
        equity_fig = go.Figure()
        equity_fig.add_trace(go.Scatter(x=dates, y=equity, mode='lines', name='Equity'))
        equity_fig.update_layout(
            title="Equity Curve",
            template="plotly_dark",
            height=300
        )
        
        # Mock recent trades
        recent_trades = dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Time"),
                    html.Th("Pair"),
                    html.Th("Action"),
                    html.Th("P&L")
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td("10:30"),
                    html.Td("EURUSD"),
                    html.Td("BUY"),
                    html.Td("R 150", style={"color": "green"})
                ]),
                html.Tr([
                    html.Td("09:15"),
                    html.Td("GBPUSD"),
                    html.Td("SELL"),
                    html.Td("R -75", style={"color": "red"})
                ])
            ])
        ], striped=True, size="sm")
        
        return balance, open_trades, win_rate, daily_pnl, equity_fig, recent_trades
        
    except Exception as e:
        return "Error", "Error", "Error", "Error", {}, html.Div(f"Error: {str(e)}")

# Callback for prop firm status
@app.callback(
    [Output("prop-firm-status", "children"),
     Output("daily-limits", "children"),
     Output("prop-firm-rules", "children"),
     Output("prop-firm-badge", "children"),
     Output("prop-firm-badge", "color")],
    [Input("prop-firm-interval", "n_intervals"),
     Input("detect-btn", "n_clicks")]
)
def update_prop_firm_status(n, detect_clicks):
    try:
        # Mock prop firm status
        is_prop_firm = detect_clicks and detect_clicks > 0
        
        if is_prop_firm:
            status = dbc.Alert([
                html.H5("🏢 FTMO Account Detected", className="alert-heading"),
                html.P("Prop firm mode is ACTIVE. All trades are subject to FTMO rules."),
                html.Hr(),
                html.P("Account: Challenge Account #12345", className="mb-0")
            ], color="warning")
            
            limits = html.Div([
                dbc.Progress("Daily Loss: R 150 / R 500", value=30, color="warning", className="mb-2"),
                dbc.Progress("Weekly Loss: R 400 / R 2000", value=20, color="info", className="mb-2"),
                dbc.Progress("Monthly Loss: R 1200 / R 5000", value=24, color="success"),
            ])
            
            rules = dbc.ListGroup([
                dbc.ListGroupItem("✅ Max Daily Loss: R 500"),
                dbc.ListGroupItem("✅ Max Risk per Trade: 1%"),
                dbc.ListGroupItem("✅ Trading Sessions: London, New York"),
                dbc.ListGroupItem("⚠️ News Avoidance: 30 minutes"),
                dbc.ListGroupItem("✅ Max Open Positions: 3"),
            ])
            
            badge_text = "FTMO Active"
            badge_color = "warning"
        else:
            status = dbc.Alert([
                html.H5("No Prop Firm Detected", className="alert-heading"),
                html.P("Standard retail account rules apply."),
            ], color="info")
            
            limits = html.P("No prop firm limits active")
            rules = html.P("Standard trading rules apply")
            badge_text = "Retail Account"
            badge_color = "info"
        
        return status, limits, rules, badge_text, badge_color
        
    except Exception as e:
        error_msg = html.Div(f"Error loading prop firm status: {str(e)}")
        return error_msg, error_msg, error_msg, "Error", "danger"

# Callback for system monitoring
@app.callback(
    [Output("cpu-chart", "figure"),
     Output("memory-chart", "figure"),
     Output("system-health", "children"),
     Output("health-badge", "color")],
    [Input("resource-interval", "n_intervals")]
)
def update_system_monitor(n):
    try:
        # Mock system data
        times = pd.date_range(start=datetime.now() - timedelta(minutes=30), periods=30, freq='1min')
        cpu_data = np.random.uniform(20, 80, 30)
        memory_data = np.random.uniform(40, 70, 30)
        
        # CPU Chart
        cpu_fig = go.Figure()
        cpu_fig.add_trace(go.Scatter(x=times, y=cpu_data, mode='lines', name='CPU %', line=dict(color='orange')))
        cpu_fig.update_layout(
            title="CPU Usage (%)",
            template="plotly_dark",
            height=250,
            yaxis=dict(range=[0, 100])
        )
        
        # Memory Chart
        memory_fig = go.Figure()
        memory_fig.add_trace(go.Scatter(x=times, y=memory_data, mode='lines', name='Memory %', line=dict(color='blue')))
        memory_fig.update_layout(
            title="Memory Usage (%)",
            template="plotly_dark",
            height=250,
            yaxis=dict(range=[0, 100])
        )
        
        # System Health
        current_cpu = cpu_data[-1]
        current_memory = memory_data[-1]
        
        if current_cpu > 90 or current_memory > 90:
            health_status = "critical"
            health_color = "danger"
            health_alert = dbc.Alert("System resources critically high!", color="danger")
        elif current_cpu > 75 or current_memory > 75:
            health_status = "warning"
            health_color = "warning"
            health_alert = dbc.Alert("System resources elevated", color="warning")
        else:
            health_status = "healthy"
            health_color = "success"
            health_alert = dbc.Alert("System running normally", color="success")
        
        health_content = html.Div([
            health_alert,
            html.P(f"CPU: {current_cpu:.1f}% | Memory: {current_memory:.1f}%"),
            html.P(f"Uptime: {n} minutes"),
        ])
        
        return cpu_fig, memory_fig, health_content, health_color
        
    except Exception as e:
        error_fig = go.Figure()
        error_content = html.Div(f"Error: {str(e)}")
        return error_fig, error_fig, error_content, "danger"

if __name__ == "__main__":
    print("🚀 Starting Enhanced Trading Dashboard...")
    app.run(debug=True, port=8050)