up:
	docker compose up -d

restart:
	docker compose down
	docker compose up -d

rebuild:
	docker compose down
	docker compose up -d --build

lint:
	echo "Running lint checks..."
	ruff check src tests
	ruff format src tests --check
	flake8 src tests --config setup.cfg

lint_fix:
	echo "Running lint fixes..."
	ruff check src tests --fix
	ruff format src tests
	flake8 src tests --config setup.cfg
	python -m mypy
