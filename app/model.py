from __future__ import annotations

import os
import json
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

from .config import MODEL_DIR, DATA_DIR, TRAIN_TEST_SPLIT_YEAR, MIN_YEARS_REQUIRED


@dataclass
class CountryModel:
	country_code: int
	country_name: str
	latest_year: int
	mae_on_holdout: Optional[float]
	coef_: Optional[float]
	intercept_: Optional[float]

	def predict(self, year: float) -> float:
		if self.coef_ is None or self.intercept_ is None:
			raise ValueError("Model weights not set")
		return float(self.coef_ * year + self.intercept_)


class EnergyIntensityEstimator:
	"""Fits simple linear models per country on energy intensity vs year.

	The target is the reported 'value' of SDG 7.3.1 per country-year. We then enable
	predicting the next year's value or any provided year per country.
	"""

	def __init__(self) -> None:
		self.country_code_to_model: Dict[int, CountryModel] = {}
		self.metadata: Dict[str, str] = {}

	@staticmethod
	def _ensure_dirs() -> None:
		os.makedirs(MODEL_DIR, exist_ok=True)
		os.makedirs(DATA_DIR, exist_ok=True)

	def fit_from_dataframe(self, df: pd.DataFrame) -> None:
		self._ensure_dirs()
		# Persist raw data snapshot
		csv_path = os.path.join(DATA_DIR, "sdg_7_3_1.csv")
		df.to_csv(csv_path, index=False)

		# Basic cleaning
		df = df.dropna(subset=["geoAreaCode", "geoAreaName", "year", "value"]).copy()
		df = df[(df["year"] >= 1990) & (df["year"] <= 2100)]

		self.country_code_to_model.clear()
		for country_code, g in df.groupby("geoAreaCode"):
			country_name = str(g["geoAreaName"].iloc[0]) if "geoAreaName" in g.columns else str(country_code)
			g = g.sort_values("year")
			if g.shape[0] < MIN_YEARS_REQUIRED:
				continue

			# Train/test split by year
			train = g[g["year"] <= TRAIN_TEST_SPLIT_YEAR]
			test = g[g["year"] > TRAIN_TEST_SPLIT_YEAR]
			if train.shape[0] < 2:
				continue

			X_train = train[["year"]].values.astype(float)
			y_train = train["value"].values.astype(float)
			model = LinearRegression()
			model.fit(X_train, y_train)

			mae = None
			if test.shape[0] > 0:
				X_test = test[["year"]].values.astype(float)
				y_test = test["value"].values.astype(float)
				y_pred = model.predict(X_test)
				mae = float(mean_absolute_error(y_test, y_pred))

			country_model = CountryModel(
				country_code=int(country_code),
				country_name=country_name,
				latest_year=int(g["year"].max()),
				mae_on_holdout=mae,
				coef_=float(model.coef_[0]),
				intercept_=float(model.intercept_),
			)
			self.country_code_to_model[int(country_code)] = country_model

		# Save model index as JSON
		index_path = os.path.join(MODEL_DIR, "energy_intensity_models.json")
		with open(index_path, "w", encoding="utf-8") as f:
			json.dump({k: vars(v) for k, v in self.country_code_to_model.items()}, f, ensure_ascii=False, indent=2)

	def load(self) -> bool:
		index_path = os.path.join(MODEL_DIR, "energy_intensity_models.json")
		if not os.path.exists(index_path):
			return False
		with open(index_path, "r", encoding="utf-8") as f:
			data = json.load(f)
		self.country_code_to_model = {int(k): CountryModel(**v) for k, v in data.items()}
		return True

	def predict(self, country_code: int, year: Optional[int] = None) -> Dict[str, float]:
		if not self.country_code_to_model:
			raise ValueError("Model not loaded/fitted")
		if country_code not in self.country_code_to_model:
			raise KeyError(f"No model for country_code={country_code}")
		country_model = self.country_code_to_model[country_code]
		target_year = year if year is not None else (country_model.latest_year + 1)
		value = country_model.predict(float(target_year))
		return {
			"country_code": float(country_code),
			"country_name": country_model.country_name,
			"year": float(target_year),
			"predicted_energy_intensity": float(value),
			"mae_on_holdout": float(country_model.mae_on_holdout) if country_model.mae_on_holdout is not None else None,
		}