format:
	pipenv run black .

export-local:
	pipenv run python extract-last-measurement.py