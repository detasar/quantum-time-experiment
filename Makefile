.PHONY: test theorem c0 c1 c2 c2-figure g2-batch1 c3 c4 c5 g2-batch2 g2 q301 q302 q303 q304 q305 g3 g4-readiness h401-archive h401-draft h401-freeze h402-isa h403-dry-run h501-dry-run h501-execute h501-retrieve h502 h503 q3-figure a601 a602 a603 ghz reproduce qpu-dry

test:
	PYTHONPATH=src pytest -q

theorem:
	PYTHONPATH=src python -m objective_clocks.cli theorem-check

c0:
	PYTHONPATH=src python scripts/run_c201.py

c1:
	PYTHONPATH=src python scripts/run_c202.py

c2:
	PYTHONPATH=src python scripts/run_c203.py

c2-figure:
	PYTHONPATH=src python scripts/run_c2_order_figure.py

g2-batch1:
	PYTHONPATH=src python scripts/run_g2_batch1.py

c3:
	PYTHONPATH=src python scripts/run_c3.py

c4:
	PYTHONPATH=src python scripts/run_c205.py

c5:
	PYTHONPATH=src python scripts/run_c206.py

g2-batch2:
	PYTHONPATH=src python scripts/run_g2_batch2.py

g2:
	PYTHONPATH=src python scripts/run_g2_all.py

q301:
	PYTHONPATH=src python scripts/run_q301.py

q302:
	PYTHONPATH=src python scripts/run_q302.py

q303:
	PYTHONPATH=src python scripts/run_q303.py

q304:
	PYTHONPATH=src python scripts/run_q304.py

q305:
	PYTHONPATH=src python scripts/run_q305_backend_amendment.py

g3:
	PYTHONPATH=src python scripts/run_g3.py

g4-readiness:
	PYTHONPATH=src python scripts/run_g4_readiness.py

h401-archive:
	PYTHONPATH=src python scripts/run_h401_archive.py

h401-draft:
	PYTHONPATH=src python scripts/run_h401_draft.py

h401-freeze:
	PYTHONPATH=src python scripts/run_h401_freeze.py

h402-isa:
	PYTHONPATH=src python scripts/run_h402_isa.py

h403-dry-run:
	PYTHONPATH=src python scripts/run_h403_dry_run.py

h501-dry-run:
	PYTHONPATH=src python scripts/run_h501_execute.py --dry-run

h501-execute:
	ALLOW_QPU_EXECUTION=YES PYTHONPATH=src python scripts/run_h501_execute.py --execute

h501-retrieve:
	PYTHONPATH=src python scripts/run_h501_retrieve.py --job-id $(JOB_ID)

h502:
	PYTHONPATH=src python scripts/run_h502_raw_analysis.py

h503:
	PYTHONPATH=src python scripts/run_h503_mitigated_analysis.py

q3-figure:
	PYTHONPATH=src python scripts/run_q3_hardware_figure.py

a601:
	PYTHONPATH=src python scripts/run_a601.py

a602:
	PYTHONPATH=src python scripts/run_a602.py

a603:
	PYTHONPATH=src python scripts/run_a603_reproducibility.py

ghz:
	PYTHONPATH=src python -m objective_clocks.cli ghz-exact

reproduce:
	PYTHONPATH=src python scripts/reproduce_all.py

qpu-dry:
	@echo "QPU execution is disabled. Complete G4 and set ALLOW_QPU_EXECUTION=YES only after human approval."
