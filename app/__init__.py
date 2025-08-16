from flask import Flask, jsonify, request

from .service import EnergyService
from .config import HOST, PORT, DEBUG


def create_app() -> Flask:
	app = Flask(__name__)
	service = EnergyService()
	service.load()

	@app.get("/health")
	def health():
		return jsonify({"status": "ok"})

	@app.post("/refresh")
	def refresh():
		stats = service.refresh()
		return jsonify({"status": "refreshed", **stats})

	@app.post("/predict")
	def predict():
		payload = request.get_json(force=True, silent=True) or {}
		country_code = payload.get("country_code")
		year = payload.get("year")
		if country_code is None:
			return jsonify({"error": "country_code is required"}), 400
		try:
			country_code_int = int(country_code)
			year_int = int(year) if year is not None else None
			result = service.predict(country_code_int, year_int)
			return jsonify(result)
		except KeyError as e:
			return jsonify({"error": str(e)}), 404
		except Exception as e:
			return jsonify({"error": str(e)}), 400

	return app


app = create_app()

if __name__ == "__main__":
	app.run(host=HOST, port=PORT, debug=DEBUG)