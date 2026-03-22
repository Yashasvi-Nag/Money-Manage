class TransactionClassifier:
    def classify(self, description, amount_str=""):
        desc = description.lower()
        if "payment" in desc:
            return "payment"
        if "cashback reversal" in desc:
            return "cashback_reversal"
        if "cashback" in desc:
            return "cashback"
        if "emi" in desc:
            return "emi"
        if amount_str:
            if str(amount_str).startswith("+"):
                return "refund"
            try:
                if float(amount_str) < 0:
                    return "refund"
            except (ValueError, TypeError):
                pass
        return "expense"
