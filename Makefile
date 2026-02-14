.PHONY: run-tests run-tests-cov

run-tests:
	pytest -v --disable-warnings

run-tests-cov:
	pytest --cov-report=html --cov=src