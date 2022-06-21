import pytest

from app.calculations import add, BankAccount , InsufficientFunds


###############################################################


# define Fixtures - those are functions that save us to do same functionality over and over between test
# we can pass to a test the fixture to run it before the test begin.

@pytest.fixture
def zero_bank_account():
    print("creating empty bank account")
    return BankAccount()


@pytest.fixture
def bank_account():
    return BankAccount(50)


##############################################################


def test_add():
    print(f"testing add function 3+5")
    assert add(3, 5) == 8


# using parametrized to run the same test with different numbers
@pytest.mark.parametrize("num1, num2, expected", [
    (2, 3, 5),
    (7, 1, 8),
    (12, 4, 16)

])
def test_add2(num1, num2, expected):
    assert add(num1, num2) == expected


# using the Fixture to run before each test and pass it as a parameter

def test_bank_set_initial_amount(bank_account):
    assert bank_account.balance == 50


def test_bank_default_amount(zero_bank_account):
    print("testing my bank account")
    assert zero_bank_account.balance == 0


def test_withdraw(bank_account):
    bank_account.withdraw(30)
    assert bank_account.balance == 20


def test_deposit(bank_account):
    bank_account.deposit(30)
    assert bank_account.balance == 80


def test_collect_interest(bank_account):
    bank_account.collect_interest()
    # round with 6 digits decimal pont
    assert round(bank_account.balance, 6) == 55


# using parametrized and fixure to test

@pytest.mark.parametrize("deposited, withdrew, expected", [
    (200, 100, 100),
    (50, 10, 40),
    (1200, 200, 1000)
])
def test_bank_transaction(zero_bank_account, deposited, withdrew, expected):
    zero_bank_account.deposit(deposited)
    zero_bank_account.withdraw(withdrew)
    assert zero_bank_account.balance == expected


# test for insufficient funds
# we expect Exception here so this is the way to expect this exception from a test
def test_insufficient_funds(bank_account):
    with pytest.raises(InsufficientFunds):
        bank_account.withdraw(200)