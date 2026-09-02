PYTHON ?= python3

.PHONY: turbo validate gaps timeline map stats export-all orphans conflicts low-confidence network prosopography dashboard backup smart-commit release

turbo: validate gaps timeline map stats
validate:
	$(PYTHON) scripts/validate.py .
gaps:
	$(PYTHON) scripts/gap_detector.py .
timeline:
	$(PYTHON) scripts/timeline_builder.py .
map:
	$(PYTHON) scripts/map_builder.py .
stats:
	$(PYTHON) scripts/stats.py .
orphans:
	$(PYTHON) scripts/gap_detector.py . --type ORPHAN_FACT
conflicts:
	$(PYTHON) scripts/gap_detector.py . --type CONFLICT_DATE
low-confidence:
	$(PYTHON) scripts/gap_detector.py . --type LOW_CONFIDENCE_CLUSTER
network:
	$(PYTHON) scripts/graph_viz.py .
prosopography:
	$(PYTHON) scripts/prosopography.py .
export-all:
	$(PYTHON) scripts/export_rdf.py .
dashboard:
	$(PYTHON) historianos_cli.py dashboard serve --port 8080
a backup:
	bash scripts/backup.sh
smart-commit:
	bash scripts/smart_commit.sh
release:
	$(PYTHON) scripts/release.py .
