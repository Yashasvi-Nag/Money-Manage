from finance.analytics.financial import FinancialAnalytics


class ScenarioSimulator:
    def __init__(self, db):
        self.db = db
        self.analytics = FinancialAnalytics(db)

    def simulate_new_emi(self, name, amount, months, liquid_money=None):
        burn_rate = self.analytics.get_burn_rate()
        new_burn = burn_rate + amount
        result = {
            "scenario": "new_emi",
            "name": name,
            "emi_amount": amount,
            "new_burn_rate": new_burn,
        }
        if liquid_money is not None:
            result["runway_impact"] = liquid_money / new_burn if new_burn > 0 else float("inf")
        return result

    def simulate_expense_reduction(self, percent):
        burn_rate = self.analytics.get_burn_rate()
        new_burn = burn_rate * (1 - percent / 100)
        return {
            "scenario": "expense_reduction",
            "percent": percent,
            "new_burn_rate": new_burn,
        }

    def simulate_no_income(self, liquid_money):
        burn_rate = self.analytics.get_burn_rate()
        runway = liquid_money / burn_rate if burn_rate > 0 else float("inf")
        return {
            "scenario": "no_income",
            "liquid_money": liquid_money,
            "burn_rate": burn_rate,
            "runway_months": runway,
        }

    def simulate_all(self, liquid_money):
        return [
            self.simulate_no_income(liquid_money),
            self.simulate_expense_reduction(10),
            self.simulate_new_emi("hypothetical_emi", 5000, 12, liquid_money),
        ]
