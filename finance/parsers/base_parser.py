import re
import datetime
from abc import ABC, abstractmethod

# Shared regex for credit card transaction lines (date, description, amount, optional Cr flag).
# The amount group requires digits, optional thousands commas, a decimal point, and exactly two
# decimal digits (e.g. "1,234.56") so the non-greedy description group cannot accidentally
# consume the amount.
CC_TRANSACTION_PATTERN = (
    r'(\d{2}\s+\w{3}\s+\d{4}|\d{2}/\d{2}/\d{4})'   # date
    r'\s+(.+?)'                                         # description (non-greedy)
    r'\s+(\d[\d,]*\.\d{2})'                            # amount: must start with a digit
    r'(Cr)?'                                            # optional credit flag
)
# Shared regex for total purchases / total debits line on credit card statements
CC_TOTAL_PATTERN = r'(?:total\s+purchases?|total\s+debits?)[:\s]+([\d,]+\.\d{2})'


def read_pdf(filepath):
    """Extract all text from a PDF using pdfplumber, falling back to PyMuPDF."""
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except ImportError:
        pass
    import fitz
    doc = fitz.open(filepath)
    try:
        return "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()


class BaseParser(ABC):
    def parse(self, filepath):
        text = read_pdf(filepath)
        self.statement_period = self._extract_statement_period(text)
        return self._extract_transactions(text)

    def _read_pdf(self, filepath):
        return read_pdf(filepath)

    @abstractmethod
    def _extract_transactions(self, text):
        raise NotImplementedError

    def _extract_statement_period(self, text):
        pattern = r'(?:statement\s+period|billing\s+period|period)[:\s]+([A-Za-z0-9\s,/-]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _normalize_date(self, date_str, formats=("%d %b %Y", "%d/%m/%Y", "%d-%m-%Y")):
        date_str = date_str.strip()
        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return date_str


class CreditCardParser(BaseParser):
    """Shared implementation for HDFC credit card statement parsers.

    Concrete subclasses (e.g. RegaliaParser, SwiggyCardParser) inherit this
    logic and may override it to handle card-specific format variations.
    """

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
