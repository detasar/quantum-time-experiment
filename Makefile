.PHONY: test theorem c0 c1 c2 g2-batch1 c3 c4 c5 g2-batch2 g2 q301 q302 q303 q304 g3 g4-readiness h401-draft a601 ghz reproduce qpu-dry

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

g3:
	PYTHONPATH=src python scripts/run_g3.py

g4-readiness:
	PYTHONPATH=src python scripts/run_g4_readiness.py

h401-draft:
	PYTHONPATH=src python scripts/run_h401_draft.py

a601:
	PYTHONPATH=src python scripts/run_a601.py

ghz:
	PYTHONPATH=src python -m objective_clocks.cli ghz-exact

reproduce:
	PYTHONPATH=src python scripts/reproduce_all.py

qpu-dry:
	@echo "QPU execution is disabled. Complete G4 and set ALLOW_QPU_EXECUTION=YES only after human approval."
