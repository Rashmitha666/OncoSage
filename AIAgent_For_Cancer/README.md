# Oncology AI Assistant System

A comprehensive AI system for oncologists specializing in lung cancer treatment, featuring multiple specialized agents to provide real-time insights, research updates, and clinical decision support.

## Features

The system consists of six specialized AI agents:

1. **Clinical News & Research Update Agent**
   - Keeps oncologists updated with the latest lung cancer research, trials, and therapies
   - Monitors medical journals, clinical trial databases, and research publications

2. **Clinical Trials Recommendation Agent**
   - Finds active lung cancer trials suitable for a given patient profile
   - Matches patient characteristics (biomarkers, cancer type, location) with trial eligibility criteria

3. **Literature Insight Agent**
   - Reads medical papers and extracts key takeaways
   - Summarizes research findings and clinical implications

4. **Voice-Activated Medical Assistant**
   - Allows doctors to ask questions like "What's the latest on EGFR-targeted therapy?"
   - Provides spoken and text responses with up-to-date information

5. **Twitter/X Research Trends Monitor Agent**
   - Scans verified medical accounts (oncologists, pharma companies) for breaking news on lung cancer
   - Identifies trending topics and discussions in the oncology community

6. **Drug Safety Alert Agent**
   - Monitors FDA/EMA websites for new warnings or recalls for lung cancer drugs
   - Detects adverse effect reports or black-box warnings
   - Notifies doctors via dashboard or SMS/email

## System Architecture

The system is built with a modular architecture where each agent operates independently but can share information through a central system. The main components are:

- **Agents**: Specialized AI modules for specific tasks
- **Utilities**: Shared functionality like API clients, NLP processing, and notification services
- **Web Dashboard**: Interactive interface to view insights and alerts
- **Voice Interface**: Natural language processing for voice commands and responses

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- API keys for various services (Twitter, PubMed, etc.)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/oncology-ai-assistant.git
   cd oncology-ai-assistant
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up configuration:
   - Create configuration files in the `config` directory
   - Add your API keys and preferences

### Configuration

Create the following configuration files in the `config` directory:

- `system_config.json`: Main system configuration
- `news_research_config.json`: News research agent configuration
- `clinical_trials_config.json`: Clinical trials agent configuration
- `literature_insight_config.json`: Literature insight agent configuration
- `twitter_trends_config.json`: Twitter trends agent configuration
- `drug_safety_config.json`: Drug safety agent configuration
- `voice_assistant_config.json`: Voice assistant configuration

Example `system_config.json`:
```json
{
  "enable_voice_assistant": true,
  "update_frequency_hours": 24,
  "notification_methods": ["dashboard", "email"],
  "notification_recipients": ["doctor@hospital.org"],
  "web_dashboard_port": 8050
}
```

## Usage

### Running the System

To start the entire system with the web dashboard:

```
python main.py
```

To start with specific options:

```
python main.py --no-dashboard  # Run without the web dashboard
python main.py --voice  # Enable voice assistant
python main.py --config custom_config.json  # Use a custom configuration file
```

### Web Dashboard

The web dashboard provides an interactive interface to:
- View the latest research and news
- Search for clinical trials matching patient profiles
- Analyze medical papers
- Monitor social media trends
- Track drug safety alerts

Access the dashboard at `http://localhost:8050` after starting the system.

### Voice Assistant

The voice assistant can be used to:
- Ask questions about lung cancer research and treatments
- Get summaries of recent papers
- Find clinical trials for patients
- Check for drug safety alerts

Example commands:
- "What's the latest on EGFR-targeted therapy?"
- "Find clinical trials for a 65-year-old female with EGFR-positive NSCLC"
- "Summarize the recent paper on osimertinib resistance"

## Development

### Project Structure

```
oncology-ai-assistant/
├── agents/                 # AI agent modules
│   ├── news_research_agent.py
│   ├── clinical_trials_agent.py
│   ├── literature_insight_agent.py
│   ├── voice_assistant_agent.py
│   ├── twitter_trends_agent.py
│   └── drug_safety_agent.py
├── utils/                  # Shared utilities
│   ├── api_clients.py
│   ├── nlp_processor.py
│   ├── document_parser.py
│   ├── notification.py
│   ├── patient_profile.py
│   └── geo_utils.py
├── web/                    # Web dashboard
│   ├── dashboard.py
│   ├── assets/
│   └── components/
├── config/                 # Configuration files
├── data/                   # Data storage
│   ├── cache/
│   └── results/
├── main.py                 # Main application
└── requirements.txt        # Dependencies
```

### Adding New Features

To add a new agent or feature:
1. Create a new module in the appropriate directory
2. Update the main system to integrate the new component
3. Add any necessary configuration options
4. Update the web dashboard if needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Medical data sources: PubMed, ClinicalTrials.gov, FDA, EMA
- Libraries and frameworks: NLTK, spaCy, Dash, Plotly, etc.
