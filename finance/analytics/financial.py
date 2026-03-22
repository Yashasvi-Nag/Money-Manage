from datetime import datetime
from finance.transactions.normalizer import TransactionNormalizer

# Goals are considered feasible when their required monthly saving is less than
# this fraction of the current burn rate (i.e. savings fit within 50% of expenses).
SAVINGS_THRESHOLD_RATIO = 0.5


class FinancialAnalytics:
    def __init__(self, db):
        self.db = db
        self.normalizer = TransactionNormalizer()

    def get_burn_rate(self):
        now = datetime.now()
        monthly_totals = []
        for i in range(3):
            # Decrement month properly using calendar arithmetic to avoid edge cases
            month = now.month - i
            year = now.year
            if month <= 0:
                month += 12
                year -= 1
            txns = self.db.get_transactions(year=year, month=month)
            total = self.normalizer.compute_total_spend(txns)
            monthly_totals.append(total)
        avg_expense = sum(monthly_totals) / 3 if monthly_totals else 0.0
        liabilities = self.db.get_liabilities()
        monthly_liabilities = sum(l.get("monthly_equivalent", 0) or 0 for l in liabilities)
        return avg_expense + monthly_liabilities

    def get_runway(self, liquid_money):
        burn_rate = self.get_burn_rate()
        if burn_rate > 0:
            return liquid_money / burn_rate
        return float("inf")

    def get_goal_feasibility(self, goal_name):
        goals = self.db.get_goals()
        goal = next((g for g in goals if g["name"] == goal_name), None)
        if not goal:
            return None
        burn_rate = self.get_burn_rate()
        required = goal["target_amount"] / goal["timeline_months"] if goal["timeline_months"] else float("inf")
        return {
            "goal": goal_name,
            "target": goal["target_amount"],
            "months": goal["timeline_months"],
            "required_monthly_saving": required,
            "current_burn_rate": burn_rate,
            "feasible": required < burn_rate * SAVINGS_THRESHOLD_RATIO,
        }

    def get_net_worth(self):
        assets = self.db.get_assets()
        liabilities = self.db.get_liabilities()
        total_assets = sum(a.get("value", 0) or 0 for a in assets)
        total_liabilities = sum(l.get("total_amount", 0) or 0 for l in liabilities)
        return total_assets - total_liabilities
