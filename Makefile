.PHONY: run-tests run-tests-cov

run-tests:
	. .venv/bin/activate && pytest -v

run-tests-cov:
	. .venv/bin/activate && pytest --cov-report=html --cov=src