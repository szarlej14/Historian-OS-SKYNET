PYTHON ?= python3
VAULT ?= .

.PHONY: init turbo validate gaps timeline map stats export-all orphans conflicts low-confidence network prosopography dashboard backup smart-commit release

init:
	@echo "Use install_historianos.py $(VAULT) to create a vault."

turbo: validate gaps timeline map stats
validate:; $(PYTHON) scripts/validate.py $(VAULT)
gaps:; $(PYTHON) scripts/gap_detector.py $(VAULT)
timeline:; $(PYTHON) scripts/timeline_builder.py $(VAULT)
map:; $(PYTHON) scripts/map_builder.py $(VAULT)
stats:; $(PYTHON) scripts/stats.py $(VAULT)
orphans:; $(PYTHON) scripts/gap_detector.py $(VAULT) --type ORPHAN_FACT
conflicts:; $(PYTHON) scripts/gap_detector.py $(VAULT) --type CONFLICT_DATE
low-confidence:; $(PYTHON) scripts/gap_detector.py $(VAULT) --type LOW_CONFIDENCE_CLUSTER
network:; $(PYTHON) scripts/graph_viz.py $(VAULT)
prosopography:; $(PYTHON) scripts/prosopography.py $(VAULT)
export-all:; $(PYTHON) scripts/export_rdf.py $(VAULT)
dashboard:; $(PYTHON) api_server.py
backup:; bash scripts/backup.sh
smart-commit:; bash scripts/smart_commit.sh
release:; $(PYTHON) scripts/release.py $(VAULT)

ledger:
	$(PYTHON) scripts/conflict_ledger.py $(DB) list
triage:
	$(PYTHON) scripts/triage.py $(DB)
export-triage:
	$(PYTHON) scripts/export_triage.py $(DB) $(TRIAGE)
sync-obsidian:
	$(PYTHON) scripts/sync_obsidian.py $(DB) $(TRIAGE)
