from sqlalchemy import text

from app.db.session import SessionLocal
from app.db.seed import seed


def reset_demo():
    db = SessionLocal()

    try:
        # Delete child/dependent records first.
        tables = [
            "agent_executions",
            "aml_investigations",
            "aml_alert_events",
            "aml_alert_transactions",
            "aml_alerts",
            "transactions",
        ]

        for table in tables:
            db.execute(text(f"DELETE FROM {table}"))

        # Reset account balances to the original demo seed values.
        db.execute(
            text("""
                UPDATE accounts
                SET balance = CASE account_id
                    WHEN 'AI-ACC-1842' THEN 2500000.00
                    WHEN 'BANKB-ACC-5276' THEN 1000000.00
                    ELSE balance
                END
                WHERE account_id IN ('AI-ACC-1842', 'BANKB-ACC-5276')
            """)
        )

        db.commit()

        # Ensure the two seed accounts exist.
        seed(db)

        print("FULL DEMO RESET COMPLETE")
        print("AI-ACC-1842  -> ₹2,500,000.00")
        print("BANKB-ACC-5276 -> ₹1,000,000.00")
        print("Transactions  -> 0")
        print("AML alerts    -> 0")
        print("Investigations -> 0")
        print("Agent executions -> 0")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    reset_demo()