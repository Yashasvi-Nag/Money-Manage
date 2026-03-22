from finance.parsers.regalia_parser import RegaliaParser
from finance.parsers.swiggy_parser import SwiggyCardParser
from finance.parsers.bank_parser import BankStatementParser


class ParserFactory:
    @staticmethod
    def get_parser(statement_type):
        mapping = {
            "HDFC_CC_REGALIA": RegaliaParser,
            "HDFC_CC_SWIGGY": SwiggyCardParser,
            "HDFC_BANK": BankStatementParser,
            "SBI_BANK": BankStatementParser,
        }
        cls = mapping.get(statement_type, BankStatementParser)
        return cls()
