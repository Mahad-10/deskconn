.PHONY: deps start clean

deps:
	pip install -r requirements.txt

server:
	python3 -u server.py

session:
	python3 -u session.py

pair:
	python3 -u pair.py
