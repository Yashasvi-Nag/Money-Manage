from finance.transactions.normalizer import TransactionNormalizer
from finance.validation.validator import ValidationEngine


def test_normalize_expense():
    n = TransactionNormalizer()
    assert n.normalize("expense", 500) == 500.0


def test_normalize_refund():
    n = TransactionNormalizer()
    assert n.normalize("refund", 200) == -200.0


def test_normalize_payment():
    n = TransactionNormalizer()
    assert n.normalize("payment", 1000) == 0.0


def test_normalize_cashback():
    n = TransactionNormalizer()
    assert n.normalize("cashback", 50) == 0.0


def test_normalize_emi():
    n = TransactionNormalizer()
    assert n.normalize("emi", 3000) == 3000.0


def test_compute_total_spend():
    n = TransactionNormalizer()
    transactions = [
        {"type": "expense", "amount": 500},
        {"type": "refund", "amount": 200},
        {"type": "payment", "amount": 1000},
        {"type": "emi", "amount": 3000},
    ]
    total = n.compute_total_spend(transactions)
    # 500 + (-200) + 0 + 3000 = 3300
    assert total == 3300.0


def test_validation_within_tolerance():
    ve = ValidationEngine()
    is_valid, diff = ve.validate(1000, 1000.5, 1.0)
    assert is_valid is True
    assert abs(diff - 0.5) < 0.001


def test_validation_outside_tolerance():
    ve = ValidationEngine()
    is_valid, diff = ve.validate(1000, 1002, 1.0)
    assert is_valid is False
    assert abs(diff - 2.0) < 0.001
