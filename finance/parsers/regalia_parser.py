import re
from finance.parsers.base_parser import BaseParser, CC_TRANSACTION_PATTERN, CC_TOTAL_PATTERN


class RegaliaParser(BaseParser):
    def __init__(self):
        self.stated_total = 0.0

    def _extract_transactions(self, text):
        transactions = []
        for match in re.finditer(CC_TRANSACTION_PATTERN, text):
            date_str, description, amount_str, cr_flag = match.groups()
            amount = float(amount_str.replace(",", ""))
            if cr_flag:
                ttype = "refund"
                amount = -amount
            else:
                ttype = "expense"
            transactions.append({
                "date": self._normalize_date(date_str),
                "description": description.strip(),
                "amount": amount,
                "transaction_type": ttype,
            })
        self.stated_total = self._extract_total_purchases(text)
        return transactions

    def _extract_total_purchases(self, text):
        match = re.search(CC_TOTAL_PATTERN, text, re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", ""))
        return 0.0
