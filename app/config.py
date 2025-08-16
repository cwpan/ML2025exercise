import os

# UN SDG API base (open)
SDG_API_BASE = os.getenv("SDG_API_BASE", "https://unstats.un.org/SDGAPI/v1/sdg")

# Indicator codes of interest (energy)
SDG_INDICATORS = {
	"energy_intensity": "7.3.1",  # Energy intensity measured in terms of primary energy and GDP
	"renewable_share": "7.2.1",   # Renewable energy share in the total final energy consumption
}

# Default training settings
TRAIN_TEST_SPLIT_YEAR = int(os.getenv("TRAIN_TEST_SPLIT_YEAR", "2018"))
MIN_YEARS_REQUIRED = int(os.getenv("MIN_YEARS_REQUIRED", "6"))

# Model persistence
MODEL_DIR = os.getenv("MODEL_DIR", "/workspace/models")
DATA_DIR = os.getenv("DATA_DIR", "/workspace/data")

# Flask settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"