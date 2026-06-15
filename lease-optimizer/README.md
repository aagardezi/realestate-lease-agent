# Vornado Penn District Lease Optimizer Agent Package

This directory contains the core agent implementation and frontend dashboard for the Vornado Penn District Lease Optimizer.

---

## 📂 Project Directory Structure

```text
lease-optimizer/
├── app/
│   ├── __init__.py
│   ├── agent.py               # Main ADK Agent and instruction prompts
│   ├── agent_runtime_app.py   # Agent Runtime interface entrypoint
│   └── tools.py               # Custom tools for BigQuery SQL & GCS PDF analysis
├── frontend/
│   └── streamlit_app.py       # Streamlit Web UI dashboard with Plotly visualisations
├── tests/
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests targeting BQ/GCS and streaming
├── pyproject.toml             # Python dependencies (Streamlit, Plotly, BigQuery, db-dtypes)
└── Dockerfile                 # Container specification for Cloud Run deployment
```

---

## 💻 Local Development & Testing

### 1. Install Dependencies
Before running the agent or frontend, install the package and its locked dependencies using `uv`:
```bash
# Set PyPI simple index override if you are in a restricted network
UV_DEFAULT_INDEX=https://pypi.org/simple agents-cli install
```

### 2. Run the Streamlit Dashboard Locally
Start the visual web interface on your local workstation:
```bash
UV_DEFAULT_INDEX=https://pypi.org/simple uv run streamlit run frontend/streamlit_app.py
```
By default, the dashboard will launch at [http://localhost:8501](http://localhost:8501).

### 3. Run the Local CLI Playground
To test the agent directly in the terminal or using the ADK dev console:
```bash
agents-cli playground
```

### 4. Execute Integration and Unit Tests
Run the automated test suite using `pytest`:
```bash
uv run pytest
```

---

## 🚀 Deployment

Refer to the main [Root README.md](../README.md) for full instructions on:
1. Uploading unstructured PDF draft leases to Google Cloud Storage.
2. Creating and seeding the mock real estate databases in BigQuery.
3. Deploying the agent to **Agent Runtime (Vertex AI Reasoning Engine)**.
4. Building and deploying the Streamlit UI to **Cloud Run** and securing it behind **Identity-Aware Proxy (IAP)**.
