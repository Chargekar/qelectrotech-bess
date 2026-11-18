.PHONY: test validate demo

test:
	python -m pytest -q

validate:
	og validate examples/sample-building.yaml --study-ready

demo:
	og compile examples/sample-building.yaml --scenario max-solar --out out/max-solar.dss
	og draw examples/sample-building.yaml --out out/concept.svg
	og draw examples/sample-building.yaml --out out/concept.pdf
	og draw examples/sample-building.yaml --out out/concept.dxf
	og propose examples/sample-building.yaml examples/upgrade-proposal.yaml --out out/proposed.yaml --audit out/change-audit.json
