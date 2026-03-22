import re
from finance.parsers.base_parser import BaseParser


class BankStatementParser(BaseParser):
    def _extract_transactions(self, text):
        transactions = []
        # Credit column pattern requires at least one digit ([\d,]*\d+\.?\d*) to prevent
        # float() from being called on an empty string when only debit is present.
        pattern = (
            r'(\d{2}[/-]\d{2}[/-]\d{4}|\d{2}\s+\w{3}\s+\d{4})'  # date
            r'\s+(.+?)'                                              # description
            r'\s+([\d,]*\d+\.?\d*)'                                 # debit (required)
            r'\s+([\d,]*\d+\.?\d*)?'                                # credit (optional)
        )
        for match in re.finditer(pattern, text):
            date_str, description, debit_str, credit_str = match.groups()
            debit = float(debit_str.replace(",", "")) if debit_str and debit_str.strip() else 0.0
            credit = float(credit_str.replace(",", "")) if credit_str and credit_str.strip() else 0.0
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
