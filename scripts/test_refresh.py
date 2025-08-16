import traceback

from app.service import EnergyService

if __name__ == "__main__":
	service = EnergyService()
	try:
		stats = service.refresh()
		print({"ok": True, **stats})
	except Exception as e:
		traceback.print_exc()
		print({"ok": False, "error": str(e)})