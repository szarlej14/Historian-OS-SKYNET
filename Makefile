PYTHON ?= python3

.PHONY: validate export temporal gaps command-center clean-check

validate:
	$(PYTHON) scripts/validate_skynet.py

temporal:
	$(PYTHON) scripts/temporal_engine.py

gaps:
	$(PYTHON) scripts/gap_prioritizer.py

command-center:
	$(PYTHON) scripts/command_center.py

export:
	@mkdir -p dist
	@echo "Preparing provenance export package..."
	@$(PYTHON) scripts/export_provenance.py
	@echo "Export complete: dist/"

clean-check:
	@$(PYTHON) -m compileall -q scripts
	@echo "Python syntax check: OK"

help:
	@echo "Historian OS SKYNET"
	@echo "  make validate        Full validation pipeline"
	@echo "  make temporal        Rebuild temporal index"
	@echo "  make gaps            Rebuild GAP priorities"
	@echo "  make command-center  Rebuild Command Center index"
	@echo "  make export          Build provenance export"
	@echo "  make clean-check     Python syntax check"
