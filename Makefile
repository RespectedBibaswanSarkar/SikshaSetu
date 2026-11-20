# SikshaSetu — Makefile (spec: /docs, /client, /hub, /pipeline, /sim, /docs)
.PHONY: seed seed-course verify serve-lan clean-cache serve hub-test client-test client-build sim

seed:            # all pinned courses (make seed-course COURSE=<slug> for one)
	python -m pipeline.run --all
seed-course:     # make seed-course COURSE=6.006
	python -m pipeline.run --course $(COURSE)
verify:
	python -m pipeline.verify
serve-lan:
	python3 -m hub.main --lan
clean-cache:
	rm -rf pipeline/cache pipeline/state

# existing v2 targets kept for back-compat
test:
	python -m pytest tests/ -v
train:
	python rl/train.py
pack:
	python packgen/build_pack.py
demo:
	python scripts/gen_questions.py
	python rl/train.py --quick
	python rl/export_policy.py
	python packgen/build_pack.py
	streamlit run dashboard/app.py
clean:
	rm -rf results/* data/questions.json packgen/*.html __pycache__ */__pycache__ */*/__pycache__
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete

serve: serve-lan
hub-test:
	python -m pytest hub/ -v
client-test:
	cd client && npx vitest run
client-build:
	cd client && npm run build
client-pack: client-build   # build PWA + starter pack (offline-pack already has sample lecture)
	@echo "Built client → client/dist; starter pack → client/public/offline-pack"
sim:
	cd sim && python sim.py --students 200
install-tauri:        # requires Rust/Cargo — see README "Install"
	cargo install --path tauri 2>/dev/null || echo "Install Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh && cargo install --path ."
install-android:      # requires Android Studio/SDK — see README "Install"
	@echo "Install Android Studio + SDK, then: cd client && npx @capacitor/cli build android"
