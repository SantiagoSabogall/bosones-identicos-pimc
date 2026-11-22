PYTHON ?= python

.PHONY: test thermal study report article all

test:
	$(PYTHON) -m pytest -q -p no:cacheprovider tests

thermal:
	$(PYTHON) src/sweep_phase3.py --N 3 4 --betas 0.1 1 10 --P 4 --steps 4000 --burn 500 --replicas 3

study:
	$(PYTHON) study_closure.py

report:
	$(PYTHON) report_closure.py
	$(PYTHON) audit_series.py
	$(PYTHON) manifest_closure.py

article:
	cd ../paper && bash build.sh

all: test report article
