import re
from finance.parsers.base_parser import BaseParser


class BankStatementParser(BaseParser):
    def _extract_transactions(self, text):
        transactions = []
        pattern = r'(\d{2}[/-]\d{2}[/-]\d{4}|\d{2}\s+\w{3}\s+\d{4})\s+(.+?)\s+([\d,]*\.?\d+)\s+([\d,]*\.?\d*)'
        for match in re.finditer(pattern, text):
            date_str, description, debit_str, credit_str = match.groups()
            debit = float(debit_str.replace(",", "")) if debit_str.strip() else 0.0
            credit = float(credit_str.replace(",", "")) if credit_str.strip() else 0.0
            if credit > 0:
                amount = -credit
                ttype = "refund"
            else:
                amount = debit
                ttype = "expense"
            transactions.append({
                "date": self._normalize_date(date_str),
                "description": description.strip(),
                "amount": amount,
                "transaction_type": ttype,
            })
        return transactions
