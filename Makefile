.PHONY: deps start clean

deps:
	pip install -r requirements.txt

system:
	python3 -u system.py

session:
	python3 -u session.py

pair:
	python3 -u pair.py
