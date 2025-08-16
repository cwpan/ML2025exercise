from typing import Optional, Dict

import pandas as pd

from .config import SDG_INDICATORS
from .sdg_client import SdgApiClient
from .model import EnergyIntensityEstimator


class EnergyService:
	def __init__(self) -> None:
		self.client = SdgApiClient()
		self.estimator = EnergyIntensityEstimator()

	def refresh(self) -> Dict[str, int]:
		indicator = SDG_INDICATORS["energy_intensity"]
		df = self.client.get_indicator_data(indicator)
		self.estimator.fit_from_dataframe(df)
		return {"num_countries": len(self.estimator.country_code_to_model), "num_rows": int(df.shape[0])}

	def load(self) -> bool:
		return self.estimator.load()

	def predict(self, country_code: int, year: Optional[int] = None) -> Dict:
		return self.estimator.predict(country_code, year)