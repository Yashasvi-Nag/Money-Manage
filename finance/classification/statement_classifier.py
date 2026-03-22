from finance.parsers.base_parser import read_pdf


class StatementClassifier:
    def classify(self, text):
        t = text.lower()
        if "regalia gold" in t or ("regalia" in t and "hdfc" in t):
            return "HDFC_CC_REGALIA"
        if "swiggy" in t and "credit card" in t:
            return "HDFC_CC_SWIGGY"
        if "hdfc" in t and "bank" in t and "statement" in t:
            return "HDFC_BANK"
        if "sbi" in t:
            return "SBI_BANK"
        return "UNKNOWN"

    def classify_file(self, filepath):
        text = read_pdf(filepath)
        return self.classify(text)
