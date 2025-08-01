#!/usr/bin/env python3
"""
Migration script for database management with Alembic.
Usage:
    python -m src.infra.migrations.migrate [command]

Commands:
    make [message]  - Create a new migration
    upgrade [rev]   - Upgrade to a later version (default: head)
    downgrade [rev] - Revert to a previous version (default: -1)
    show            - Show current revision
    history         - Show migration history
"""

import logging
import os
import sys
from pathlib import Path


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Set the current directory to the project root
PROJECT_ROOT = Path(__file__).parents[3]
os.chdir(PROJECT_ROOT)

# Import after setting the working directory
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from src.settings import settings


# Get the Alembic configuration
alembic_cfg = Config("alembic.ini")


def make_migrations(message: str | None = None) -> None:
    """Create a new migration."""
    command.revision(alembic_cfg, message=message, autogenerate=True)
    logger.info("Migration file created.")


def upgrade(revision: str = "head") -> None:
    """Upgrade to a later version."""
    command.upgrade(alembic_cfg, revision)
    logger.info("Database upgraded to %s.", revision)


def downgrade(revision: str = "-1") -> None:
    """Revert to a previous version."""
    command.downgrade(alembic_cfg, revision)
    logger.info("Database downgraded to %s.", revision)


def show_current() -> None:
    """Show current revision."""
    command.current(alembic_cfg, verbose=True)


def show_history() -> None:
    """Show migration history."""
    command.history(alembic_cfg, verbose=True)


def main() -> None:
    """Main function to parse arguments and execute commands."""
    print(settings.DATABASE_URI)
    print(settings.POSTGRES_USER)
    if len(sys.argv) < 2:
        logger.info(__doc__)
        sys.exit(1)

    command_name = sys.argv[1]

    if command_name == "make":
        message = sys.argv[2] if len(sys.argv) > 2 else None
        make_migrations(message)
    elif command_name == "upgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "head"
        upgrade(revision)
    elif command_name == "downgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
        downgrade(revision)
    elif command_name == "show":
        show_current()
    elif command_name == "history":
        show_history()
    else:
        logger.error("Unknown command: %s", command_name)
        logger.info(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
