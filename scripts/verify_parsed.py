"""Verify parsed documents and recorded parsing failures in PostgreSQL."""

import asyncio

from sqlalchemy import text

from hardenhelp.config import get_settings
from hardenhelp.db.session import make_engine


async def main() -> None:
    engine = make_engine(get_settings())

    try:
        async with engine.connect() as connection:
            documents = await connection.execute(
                text("""
                    SELECT
                        d.id,
                        d.title,
                        d.doc_type,
                        d.metadata->>'parser' AS parser,
                        COUNT(p.id) AS page_count
                    FROM documents AS d
                    LEFT JOIN pages AS p ON p.document_id = d.id
                    WHERE d.id BETWEEN 21 AND 25
                    GROUP BY d.id
                    ORDER BY d.id
                """)
            )

            print("PARSED DOCUMENTS:")
            for row in documents:
                print(row)

            failures = await connection.execute(
                text("""
                    SELECT reason, COUNT(*) AS file_count
                    FROM parse_failures
                    GROUP BY reason
                    ORDER BY reason
                """)
            )

            print("\nPARSE FAILURES:")
            rows = failures.fetchall()

            if rows:
                for row in rows:
                    print(row)
            else:
                print("No parsing failures recorded.")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
