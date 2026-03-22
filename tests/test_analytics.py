from finance.db.schema import Database
from finance.analytics.financial import FinancialAnalytics


def setup_db():
    db = Database(":memory:")
    db.connect()
    # Add some assets and liabilities
    db.insert_asset("Savings Account", 500000.0)
    db.insert_asset("Mutual Funds", 200000.0)
    db.insert_liability("Home Loan", 2000000.0, "monthly", 20000.0)
    # Add some transactions (recent months)
    from datetime import datetime
    now = datetime.now()
    ym = f"{now.year}-{now.month:02d}"
    db.insert_transaction(f"{ym}-01", "Amazon purchase", 1500.0, "expense", "shopping", None)
    db.insert_transaction(f"{ym}-05", "Swiggy order", 300.0, "expense", "food", None)
    db.insert_transaction(f"{ym}-10", "EMI payment", 5000.0, "emi", "emi", None)
    return db


def test_net_worth():
    db = setup_db()
    analytics = FinancialAnalytics(db)
    net_worth = analytics.get_net_worth()
    # 700000 - 2000000 = -1300000
    assert net_worth == 700000.0 - 2000000.0
    db.close()


def test_runway_returns_number():
    db = setup_db()
    analytics = FinancialAnalytics(db)
    runway = analytics.get_runway(100000)
    assert isinstance(runway, (int, float))
    db.close()


def test_burn_rate_returns_number():
    db = setup_db()
    analytics = FinancialAnalytics(db)
    burn_rate = analytics.get_burn_rate()
    assert isinstance(burn_rate, (int, float))
    db.close()
