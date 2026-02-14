.PHONY: run-tests run-tests-cov

run-tests:
	pytest -v

run-tests-cov:
	pytest --cov-report=html --cov=src