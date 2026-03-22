from finance.classification.statement_classifier import StatementClassifier


def test_regalia_gold():
    sc = StatementClassifier()
    assert sc.classify("HDFC Regalia Gold Credit Card Statement") == "HDFC_CC_REGALIA"


def test_regalia_hdfc():
    sc = StatementClassifier()
    assert sc.classify("HDFC Regalia Credit Card") == "HDFC_CC_REGALIA"


def test_swiggy_cc():
    sc = StatementClassifier()
    assert sc.classify("Swiggy HDFC Credit Card statement") == "HDFC_CC_SWIGGY"


def test_hdfc_bank():
    sc = StatementClassifier()
    assert sc.classify("HDFC Bank Statement for account") == "HDFC_BANK"


def test_sbi_bank():
    sc = StatementClassifier()
    assert sc.classify("SBI account transactions") == "SBI_BANK"


def test_unknown():
    sc = StatementClassifier()
    assert sc.classify("random text with no known bank") == "UNKNOWN"
