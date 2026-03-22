from finance.parsers.parser_factory import ParserFactory
from finance.parsers.regalia_parser import RegaliaParser
from finance.parsers.swiggy_parser import SwiggyCardParser
from finance.parsers.bank_parser import BankStatementParser
from finance.transactions.classifier import TransactionClassifier


def test_factory_regalia():
    parser = ParserFactory.get_parser("HDFC_CC_REGALIA")
    assert isinstance(parser, RegaliaParser)


def test_factory_swiggy():
    parser = ParserFactory.get_parser("HDFC_CC_SWIGGY")
    assert isinstance(parser, SwiggyCardParser)


def test_factory_unknown():
    parser = ParserFactory.get_parser("UNKNOWN")
    assert isinstance(parser, BankStatementParser)


def test_txn_classify_payment():
    tc = TransactionClassifier()
    assert tc.classify("payment received") == "payment"


def test_txn_classify_cashback():
    tc = TransactionClassifier()
    assert tc.classify("cashback credit") == "cashback"


def test_txn_classify_cashback_reversal():
    tc = TransactionClassifier()
    assert tc.classify("cashback reversal charge") == "cashback_reversal"


def test_txn_classify_emi():
    tc = TransactionClassifier()
    assert tc.classify("emi deduction") == "emi"


def test_txn_classify_expense():
    tc = TransactionClassifier()
    assert tc.classify("amazon purchase") == "expense"
