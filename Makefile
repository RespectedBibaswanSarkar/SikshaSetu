.PHONY: demo test train pack clean

demo:
	@echo "=== Running SikshaSetu v2 Demo ==="
	python scripts/gen_questions.py
	python rl/train.py --quick
	python rl/export_policy.py
	python packgen/build_pack.py
	streamlit run dashboard/app.py

test:
	python -m pytest tests/ -v

train:
	python rl/train.py

pack:
	python packgen/build_pack.py

clean:
	rm -rf results/* data/questions.json packgen/*.html __pycache__ */__pycache__ */*/__pycache__
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete
