# SikshaSetu — Makefile (React+Vite client, FastAPI hub, SQLite content)
.PHONY: bootstrap ingest seed run serve test validate client-build clean

bootstrap:
	python3 -m pip install -r requirements.txt || true
	cd client && npm install

ingest:
	python3 -m pipeline.build_db
	python3 scripts/validate_content.py

validate:
	python3 scripts/validate_content.py

seed: ingest client-build

client-build:
	cd client && npm run build

run:
	python3 -m hub.main --lan

serve: run

test: validate
	python3 -m pytest hub/ -v
	cd client && npm test

clean:
	rm -rf client/dist __pycache__ */__pycache__
