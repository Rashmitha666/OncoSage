"""
Web dashboard for the Oncology AI Assistant System.
Displays results from all agents in an interactive web interface.
"""
import os
import json
import logging
from typing import Dict, Any
from datetime import datetime

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use a Bootstrap theme (e.g., MINTY)
app = dash.Dash(__name__, title="Oncology AI Assistant Dashboard", external_stylesheets=[dbc.themes.MINTY])

# Redesigned layout using Bootstrap components
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Oncology AI Assistant Dashboard", className="display-4 mb-2 mt-2 text-center"),
            html.P("Real-time insights for oncologists treating lung cancer patients", className="lead text-center mb-4"),
        ])
    ]),
    dbc.Tabs([
        dbc.Tab(label="Overview", tab_id="overview", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="bi bi-activity me-2"),
                            "System Status"
                        ]),
                        dbc.CardBody(html.Div(id="system-status")),
                    ], className="mb-4"),
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="bi bi-lightbulb me-2"),
                            "Latest Updates"
                        ]),
                        dbc.CardBody(html.Div(id="latest-updates")),
                    ], className="mb-4"),
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="bi bi-exclamation-triangle-fill text-danger me-2"),
                            "Urgent Alerts"
                        ]),
                        dbc.CardBody(html.Div(id="urgent-alerts")),
                    ]),
                ], width=12)
            ])
        ]),
        dbc.Tab(label="Research & News", tab_id="research", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="bi bi-journal-text me-2"),
                            "Latest Research"
                        ]),
                        dbc.CardBody(html.Div(id="latest-research")),
                    ], className="mb-4"),
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="bi bi-graph-up-arrow me-2"),
                            "Research Trends"
                        ]),
                        dbc.CardBody(dcc.Graph(id="research-trends-graph")),
                    ], className="mb-4"),
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="bi bi-book me-2"),
                            "Recent Publications"
                        ]),
                        dbc.CardBody(html.Div(id="recent-publications")),
                    ]),
                ], width=12)
            ])
        ]),
        dbc.Tab(label="Clinical Trials", tab_id="trials", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="bi bi-search me-2"),
                            "Clinical Trials Finder"
                        ]),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Cancer Type"),
                                    dcc.Dropdown(
                                        id="cancer-type-dropdown",
                                        options=[
                                            {"label": "Non-small Cell Lung Cancer (NSCLC)", "value": "nsclc"},
                                            {"label": "Small Cell Lung Cancer (SCLC)", "value": "sclc"},
                                            {"label": "All Lung Cancer Types", "value": "all"}
                                        ],
                                        value="all"
                                    ),
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Biomarker Status"),
                                    dcc.Dropdown(
                                        id="biomarker-dropdown",
                                        options=[
                                            {"label": "EGFR Mutation", "value": "egfr"},
                                            {"label": "ALK Fusion", "value": "alk"},
                                            {"label": "ROS1 Fusion", "value": "ros1"},
                                            {"label": "BRAF Mutation", "value": "braf"},
                                            {"label": "PD-L1 Expression", "value": "pdl1"},
                                            {"label": "No Specific Biomarker", "value": "none"}
                                        ],
                                        value="none"
                                    ),
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Location (City, State)"),
                                    dbc.Input(id="location-input", type="text", placeholder="e.g., Boston, MA"),
                                ], md=4),
                            ], className="mb-3"),
                            dbc.Button("Find Trials", id="find-trials-button", color="primary"),
                        ]),
                    ], className="mb-4"),
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="bi bi-list-check me-2"),
                            "Matching Trials"
                        ]),
                        dbc.CardBody(html.Div(id="matching-trials")),
                    ]),
                ], width=12)
            ])
        ]),
        dbc.Tab(label="Literature Insights", tab_id="literature", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="bi bi-file-earmark-text me-2"),
                            "Paper Analysis"
                        ]),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Paper ID or URL"),
                                    dbc.Input(id="paper-input", type="text", placeholder="PubMed ID or URL"),
                                ], md=8),
                                dbc.Col([
                                    dbc.Button("Analyze Paper", id="analyze-paper-button", color="primary", className="mt-4"),
                                ], md=4),
                            ])
                        ]),
                    ], className="mb-4"),
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="bi bi-lightbulb me-2"),
                            "Paper Insights"
                        ]),
                        dbc.CardBody(html.Div(id="paper-insights")),
                    ]),
                ], width=12)
            ])
        ]),
        dbc.Tab(label="Social Media Trends", tab_id="social", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="bi bi-twitter me-2"),
                            "Twitter/X Trends"
                        ]),
                        dbc.CardBody(dcc.Graph(id="twitter-trends-graph")),
                    ], className="mb-4"),
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="bi bi-chat-dots me-2"),
                            "Top Tweets"
                        ]),
                        dbc.CardBody(html.Div(id="top-tweets")),
                    ]),
                ], width=12)
            ])
        ]),
        dbc.Tab(label="Drug Safety", tab_id="safety", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="bi bi-shield-exclamation me-2"),
                            "Safety Alerts"
                        ]),
                        dbc.CardBody(html.Div(id="safety-alerts")),
                    ], className="mb-4"),
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="bi bi-activity me-2"),
                            "Recent Adverse Events"
                        ]),
                        dbc.CardBody(dcc.Graph(id="adverse-events-graph")),
                    ]),
                ], width=12)
            ])
        ]),
    ], id="main-tabs", active_tab="overview", className="mb-4"),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # in milliseconds (1 minute)
        n_intervals=0
    ),
    dbc.Row([
        dbc.Col([
            html.P("© 2025 Oncology AI Assistant System", className="text-center text-muted small mt-4 mb-2"),
        ])
    ])
], fluid=True)

# Define callback to update system status
@app.callback(
    Output("system-status", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_system_status(n):
    """Update the system status display."""
    return html.Div([
        html.P(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
        html.P("All systems operational"),
    ])

# Define callback to update latest updates
@app.callback(
    Output("latest-updates", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_latest_updates(n):
    """Update the latest updates display."""
    # In a real implementation, this would fetch actual data
    return html.Div([
        html.Div([
            html.H4("News & Research Update"),
            html.P("Last run: 2 hours ago"),
            html.P("Found 15 new research papers and 8 clinical trials"),
        ], className="update-card"),
        
        html.Div([
            html.H4("Twitter/X Trends Update"),
            html.P("Last run: 1 hour ago"),
            html.P("Trending topics: immunotherapy, EGFR inhibitors, lung cancer screening"),
        ], className="update-card"),
        
        html.Div([
            html.H4("Drug Safety Update"),
            html.P("Last run: 3 hours ago"),
            html.P("No new urgent safety alerts"),
        ], className="update-card"),
    ], className="updates-container")

# Define callback to update urgent alerts
@app.callback(
    Output("urgent-alerts", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_urgent_alerts(n):
    """Update the urgent alerts display."""
    # In a real implementation, this would fetch actual alerts
    # For demonstration, we'll show a sample alert
    return html.Div([
        html.Div([
            html.H4("FDA Safety Alert: Osimertinib"),
            html.P("New safety information regarding potential risk of heart failure."),
            html.A("View Details", href="#"),
        ], className="alert-card urgent"),
    ])

# Define callback to update research trends graph
@app.callback(
    Output("research-trends-graph", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_research_trends(n):
    """Update the research trends graph."""
    # Sample data for demonstration
    topics = ['Immunotherapy', 'Targeted Therapy', 'Early Detection', 
              'Biomarkers', 'Resistance Mechanisms', 'Combination Therapy']
    paper_counts = [45, 38, 22, 30, 18, 25]
    
    fig = px.bar(
        x=topics, 
        y=paper_counts,
        labels={'x': 'Research Topic', 'y': 'Number of Papers (Last 30 Days)'},
        title='Trending Research Topics in Lung Cancer'
    )
    
    return fig

# Define callback to update Twitter trends graph
@app.callback(
    Output("twitter-trends-graph", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_twitter_trends(n):
    """Update the Twitter trends graph."""
    # Sample data for demonstration
    topics = ['Immunotherapy', 'EGFR Inhibitors', 'Lung Cancer Screening', 
              'Clinical Trials', 'Survivorship', 'Side Effects Management']
    tweet_counts = [120, 85, 65, 45, 30, 55]
    
    fig = px.bar(
        x=topics, 
        y=tweet_counts,
        labels={'x': 'Topic', 'y': 'Number of Tweets (Last 7 Days)'},
        title='Trending Topics on Twitter/X'
    )
    
    return fig

# Define callback to update adverse events graph
@app.callback(
    Output("adverse-events-graph", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_adverse_events(n):
    """Update the adverse events graph."""
    # Sample data for demonstration
    drugs = ['Osimertinib', 'Pembrolizumab', 'Nivolumab', 
             'Alectinib', 'Durvalumab', 'Crizotinib']
    events = [24, 32, 28, 15, 22, 18]
    
    fig = px.bar(
        x=drugs, 
        y=events,
        labels={'x': 'Drug', 'y': 'Number of Adverse Events (Last 30 Days)'},
        title='Recent Adverse Events by Drug'
    )
    
    return fig

# Define callback to handle trial search
@app.callback(
    Output("matching-trials", "children"),
    [Input("find-trials-button", "n_clicks")],
    [dash.dependencies.State("cancer-type-dropdown", "value"),
     dash.dependencies.State("biomarker-dropdown", "value"),
     dash.dependencies.State("location-input", "value")]
)
def find_matching_trials(n_clicks, cancer_type, biomarker, location):
    """Find clinical trials matching the criteria."""
    if n_clicks is None:
        return html.P("Enter search criteria and click 'Find Trials'")
    
    # In a real implementation, this would call the clinical trials agent
    # For demonstration, we'll show sample results
    return html.Div([
        html.P(f"Found 12 trials matching your criteria:"),
        
        html.Div([
            html.H4("Phase 2 Study of Novel PD-L1 Inhibitor for NSCLC"),
            html.P("Status: Recruiting"),
            html.P("Location: Massachusetts General Hospital, Boston, MA (2.5 miles)"),
            html.P("Eligibility: Stage III/IV NSCLC, PD-L1 positive, no prior immunotherapy"),
            html.A("View Details", href="#"),
        ], className="trial-card"),
        
        html.Div([
            html.H4("Combination Therapy with EGFR-TKI and Anti-angiogenic Agent"),
            html.P("Status: Recruiting"),
            html.P("Location: Dana-Farber Cancer Institute, Boston, MA (3.1 miles)"),
            html.P("Eligibility: EGFR-mutated NSCLC, progression on first-line TKI"),
            html.A("View Details", href="#"),
        ], className="trial-card"),
        
        html.Div([
            html.H4("Novel ALK Inhibitor for ALK-positive NSCLC"),
            html.P("Status: Recruiting"),
            html.P("Location: Beth Israel Deaconess Medical Center, Boston, MA (1.8 miles)"),
            html.P("Eligibility: ALK-positive NSCLC, prior treatment with crizotinib"),
            html.A("View Details", href="#"),
        ], className="trial-card"),
    ])

# Define callback to handle paper analysis
@app.callback(
    Output("paper-insights", "children"),
    [Input("analyze-paper-button", "n_clicks")],
    [dash.dependencies.State("paper-input", "value")]
)
def analyze_paper(n_clicks, paper_id):
    """Analyze a paper and display insights."""
    if n_clicks is None or not paper_id:
        return html.P("Enter a PubMed ID or paper URL and click 'Analyze Paper'")
    
    # In a real implementation, this would call the literature insight agent
    # For demonstration, we'll show sample results
    return html.Div([
        html.H3("Osimertinib in Patients with EGFR T790M-Positive Advanced Non-Small-Cell Lung Cancer"),
        html.P("Authors: Cross DAE, Ashton SE, Ghiorghiu S, et al."),
        html.P("Journal: New England Journal of Medicine, 2017"),
        
        html.H4("Summary"),
        html.P("This study evaluated the efficacy of osimertinib in patients with EGFR T790M mutation-positive advanced non-small-cell lung cancer who had disease progression during prior EGFR-TKI therapy. The results showed that osimertinib had significantly greater efficacy than platinum therapy plus pemetrexed in patients with T790M-positive advanced non-small-cell lung cancer."),
        
        html.H4("Key Findings"),
        html.Ul([
            html.Li("Median progression-free survival was significantly longer with osimertinib (10.1 months) than with platinum-pemetrexed (4.4 months)"),
            html.Li("Objective response rate was significantly better with osimertinib (71%) than with platinum-pemetrexed (31%)"),
            html.Li("The frequency of adverse events of grade 3 or higher was lower with osimertinib (23%) than with platinum-pemetrexed (47%)"),
        ]),
        
        html.H4("Clinical Implications"),
        html.Ul([
            html.Li("Osimertinib should be considered the standard of care for patients with T790M-positive NSCLC after progression on first-line EGFR-TKI therapy"),
            html.Li("Molecular testing for T790M mutation should be performed in all patients with EGFR-mutated NSCLC who progress on first-line EGFR-TKI therapy"),
            html.Li("The favorable safety profile of osimertinib may improve quality of life for patients"),
        ]),
    ])

def start_dashboard(system, port=8050):
    """Start the dashboard server."""
    app.run(debug=True, port=port)

if __name__ == "__main__":
    app.run(debug=True)
