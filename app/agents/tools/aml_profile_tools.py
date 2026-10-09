from sqlalchemy.orm import Session

from app.repositories.aml_profiles import AMLProfileRepository


class AMLProfileTools:
    def __init__(self):
        self.repository = AMLProfileRepository()

    def get_aml_profile(self, db: Session, account_id: str):
        profile = self.repository.get(db, account_id)

        if not profile:
            raise ValueError(f"AML profile not found: {account_id}")

        return {
            "account_id": profile.account_id,
            "risk_category": profile.risk_category,
            "expected_min_transaction": profile.expected_min_transaction,
            "expected_max_transaction": profile.expected_max_transaction,
            "expected_daily_transaction_count": profile.expected_daily_transaction_count,
            "expected_monthly_volume": profile.expected_monthly_volume,
            "baseline_window_days": profile.baseline_window_days,
        }