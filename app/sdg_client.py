import os
from typing import Dict, List, Optional

import requests
import pandas as pd

from .config import SDG_API_BASE


class SdgApiClient:
	"""Minimal client for UN SDG open API."""

	def __init__(self, base_url: Optional[str] = None, session: Optional[requests.Session] = None) -> None:
		self.base_url = base_url or SDG_API_BASE
		self.session = session or requests.Session()
		self.session.headers.update({"Accept": "application/json"})

	def get_indicator_data(self, indicator_code: str, page_size: int = 1000) -> pd.DataFrame:
		"""
		Fetch indicator observations using /Indicator/Data endpoint.

		The API returns an object with pagination meta and a 'data' array. We will
		iterate pages until we reach totalPages.
		"""
		url = f"{self.base_url}/Indicator/Data"
		page = 1
		records: List[Dict] = []
		total_pages: Optional[int] = None
		while True:
			params = {"indicator": indicator_code, "page": page, "pageSize": page_size}
			resp = self.session.get(url, params=params, timeout=60)
			resp.raise_for_status()
			payload = resp.json()
			# Expect an object with 'data'
			if not isinstance(payload, dict) or "data" not in payload:
				break
			data = payload.get("data") or []
			if not isinstance(data, list) or len(data) == 0:
				break
			records.extend(data)
			# Pagination control
			total_pages = total_pages or payload.get("totalPages") or None
			if isinstance(total_pages, int) and page >= total_pages:
				break
			page += 1

		if not records:
			return pd.DataFrame(columns=["geoAreaCode", "geoAreaName", "year", "value", "series", "time_detail", "source"])  # empty with expected columns

		# Normalize JSON to DataFrame
		df = pd.json_normalize(records)
		# Map keys to a consistent schema
		rename_map = {
			"timePeriodStart": "year",
			"time_detail": "time_detail",
		}
		for src, dst in rename_map.items():
			if src in df.columns:
				df.rename(columns={src: dst}, inplace=True)

		# Build final subset
		keep_cols = [
			"geoAreaCode",
			"geoAreaName",
			"year",
			"value",
			"series",
			"time_detail",
			"source",
		]
		present_cols = [c for c in keep_cols if c in df.columns]
		df = df[present_cols].copy()

		# Type coercions
		if "year" in df.columns:
			df["year"] = pd.to_numeric(df["year"], errors="coerce")
		if "value" in df.columns:
			df["value"] = pd.to_numeric(df["value"], errors="coerce")
		if "geoAreaCode" in df.columns:
			df["geoAreaCode"] = pd.to_numeric(df["geoAreaCode"], errors="coerce")
		return df