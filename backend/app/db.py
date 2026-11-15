import logging
from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from fastapi import HTTPException, Request, status
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)

DATABASE_ERROR = {
    "code": "DATABASE_UNAVAILABLE",
    "message": "Không thể đọc dữ liệu phòng. Kiểm tra cấu hình và kết nối PostgreSQL.",
}


@contextmanager
def get_db(request: Request) -> Iterator[psycopg.Connection]:
    database_url = request.app.state.settings.database_url
    if not database_url:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=DATABASE_ERROR)
    try:
        with psycopg.connect(
            database_url,
            connect_timeout=5,
            row_factory=dict_row,
        ) as connection:
            connection.read_only = True
            connection.execute("SELECT set_config('statement_timeout', '5000', true)")
            yield connection
    except psycopg.Error as exc:
        # Driver error strings can include connection details. Log the class only.
        logger.warning("Rooms database request failed (%s)", type(exc).__name__)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail=DATABASE_ERROR
        ) from None
