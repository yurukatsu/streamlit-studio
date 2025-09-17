format:
	uv run isort . && uv run ruff format

check:
	uv run ruff check --fix

run:
	cd app && uv run streamlit run main.py --server.address=0.0.0.0 --server.port=8501
