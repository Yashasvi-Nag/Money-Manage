import re
import datetime
from abc import ABC, abstractmethod

# Shared regex for credit card transaction lines (date, description, amount, optional Cr flag)
CC_TRANSACTION_PATTERN = r'(\d{2}\s+\w{3}\s+\d{4}|\d{2}/\d{2}/\d{4})\s+(.+?)\s+([\d,]+\.\d{2})(Cr)?'
# Shared regex for total purchases / total debits line on credit card statements
CC_TOTAL_PATTERN = r'(?:total\s+purchases?|total\s+debits?)[:\s]+([\d,]+\.\d{2})'


def read_pdf(filepath):
    """Extract all text from a PDF using pdfplumber, falling back to PyMuPDF."""
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception:
        import fitz
        doc = fitz.open(filepath)
        return "\n".join(page.get_text() for page in doc)


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
