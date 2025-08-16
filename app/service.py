from typing import Optional, Dict, List

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

	def list_countries(self) -> List[Dict[str, object]]:
		items: List[Dict[str, object]] = []
		for model in self.estimator.country_code_to_model.values():
			items.append({
				"country_code": model.country_code,
				"country_name": model.country_name,
				"latest_year": model.latest_year,
			})
		items.sort(key=lambda x: str(x["country_name"]))
		return items