from finance.db.schema import Database
from finance.simulation.scenarios import ScenarioSimulator


def setup_db():
    db = Database(":memory:")
    db.connect()
    db.insert_liability("Car Loan", 500000.0, "monthly", 10000.0)
    from datetime import datetime
    now = datetime.now()
    ym = f"{now.year}-{now.month:02d}"
    db.insert_transaction(f"{ym}-01", "Grocery store", 2000.0, "expense", "food", None)
    db.insert_transaction(f"{ym}-05", "Netflix subscription", 500.0, "expense", "entertainment", None)
    return db


def test_simulate_no_income():
    db = setup_db()
    sim = ScenarioSimulator(db)
    result = sim.simulate_no_income(100000)
    assert result["scenario"] == "no_income"
    assert result["liquid_money"] == 100000
    assert "burn_rate" in result
    assert "runway_months" in result
    db.close()


def test_simulate_expense_reduction():
    db = setup_db()
    sim = ScenarioSimulator(db)
    result = sim.simulate_expense_reduction(10)
    assert result["scenario"] == "expense_reduction"
    assert result["percent"] == 10
    assert "new_burn_rate" in result
    db.close()


def test_simulate_all():
    db = setup_db()
    sim = ScenarioSimulator(db)
    results = sim.simulate_all(100000)
    assert isinstance(results, list)
    assert len(results) >= 2
    db.close()
