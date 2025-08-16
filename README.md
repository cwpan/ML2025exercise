# AI Energy Consumption Predictor (UN SDG data)

Run a Flask API that fetches UN SDG energy intensity data (Indicator 7.3.1), trains simple per-country models, and serves predictions.

## Setup

```bash
# Create venv and install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run API
python -m flask --app app run --host 0.0.0.0 --port 8000
```

## Endpoints

- GET /health
- POST /refresh
  - Downloads latest SDG 7.3.1 data and fits models
  - Response: { status, num_countries, num_rows }
- POST /predict
  - Body: { "country_code": <int>, "year"?: <int> }
  - Predicts energy intensity for requested year (defaults to latest+1)

## Example

```bash
curl -X POST http://localhost:8000/refresh
curl -X POST http://localhost:8000/predict -H 'Content-Type: application/json' -d '{"country_code": 840}'
```

Notes: Data from UN SDG API `https://unstats.un.org/SDGAPI/v1/sdg/Indicator/Data?indicator=7.3.1`.