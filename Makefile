up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose down
	docker compose up -d

rebuild:
	docker compose down
	docker compose up -d --build

lint:
	echo "Running lint checks..."
	uv run ruff check src tests
	uv run ruff format src tests --check
	uv run flake8 src tests --config setup.cfg
	uv run python -m mypy

lint_fix:
	echo "Running lint fixes..."
	uv run ruff check src tests --fix
	uv run ruff format src tests
	uv run flake8 src tests --config setup.cfg
	uv run python -m mypy

make_migrations:
	docker exec -it teacher_fastapi uv run python -m src.infra.migrations.migrate make

migrate:
	docker exec -it teacher_fastapi uv run python -m src.infra.migrations.migrate upgrade

migrate_down:
	docker exec -it teacher_fastapi uv run python -m src.infra.migrations.migrate downgrade
