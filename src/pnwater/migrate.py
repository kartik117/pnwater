"""One-shot schema creation, run once by the `migrate` service in
docker-compose before any of the four app services start.

PulsePay (a sibling project) found out the hard way that having every
service call init_db() from its own startup path means they race to
CREATE TABLE against a fresh Postgres. Applying that lesson here from
the start rather than re-discovering it.
"""

import logging

from pnwater.storage.db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    init_db()
    logger.info("schema migration complete")


if __name__ == "__main__":
    main()
