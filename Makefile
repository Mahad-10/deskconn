.PHONY: deps start clean

deps:
	pip install -r requirements.txt

start:
	python3 -u server.py
