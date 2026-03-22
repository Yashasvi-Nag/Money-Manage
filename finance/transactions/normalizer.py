class TransactionNormalizer:
    def normalize(self, transaction_type, amount):
        t = transaction_type
        if t == "expense":
            return abs(float(amount))
        if t == "refund":
            return -abs(float(amount))
        if t == "payment":
            return 0.0
        if t == "cashback":
            return 0.0
        if t == "cashback_reversal":
            return abs(float(amount))
        if t == "emi":
            return abs(float(amount))
        return abs(float(amount))

    def compute_total_spend(self, transactions):
        total = 0.0
        for txn in transactions:
            total += self.normalize(txn.get("type", "expense"), txn.get("amount", 0))
        return total
