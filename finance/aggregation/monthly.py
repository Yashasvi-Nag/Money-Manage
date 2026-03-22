from datetime import datetime
from finance.transactions.normalizer import TransactionNormalizer


class MonthlyAggregator:
    def __init__(self, db):
        self.db = db
        self.normalizer = TransactionNormalizer()

    def get_monthly_summary(self, year=None, month=None):
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        transactions = self.db.get_transactions(year=year, month=month)
        total_spend = self.normalizer.compute_total_spend(transactions)
        category_breakdown = {}
        emi_spend = 0.0
        lifestyle_cats = {"food", "travel", "entertainment"}
        lifestyle_spend = 0.0
        for txn in transactions:
            norm = self.normalizer.normalize(txn.get("type", "expense"), txn.get("amount", 0))
            cat = txn.get("category", "uncategorized") or "uncategorized"
            category_breakdown[cat] = category_breakdown.get(cat, 0.0) + norm
            if txn.get("type") == "emi":
                emi_spend += norm
            if cat in lifestyle_cats:
                lifestyle_spend += norm
        month_str = f"{year}-{month:02d}"
        return {
            "month": month_str,
            "total_spend": total_spend,
            "category_breakdown": category_breakdown,
            "emi_spend": emi_spend,
            "lifestyle_spend": lifestyle_spend,
        }

    def get_all_months_summary(self):
        transactions = self.db.get_transactions()
        months = {}
        for txn in transactions:
            date_str = txn.get("date", "")
            if date_str and len(date_str) >= 7:
                ym = date_str[:7]
                months.setdefault(ym, []).append(txn)
        summaries = []
        for ym, txns in sorted(months.items()):
            parts = ym.split("-")
            y, m = int(parts[0]), int(parts[1])
            summaries.append(self.get_monthly_summary(year=y, month=m))
        return summaries
