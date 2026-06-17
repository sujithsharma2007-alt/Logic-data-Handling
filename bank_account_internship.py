"""
OOPs Bank Account - ATM System (Internship Level)
Features:
- Multiple accounts
- Inheritance (SavingsAccount, CurrentAccount)
- Custom Exceptions
- PIN Hashing (Security)
- CSV transaction logs
- Transfer between accounts
- Interest Calculation
- Input Validation
"""

import os
import csv
import hashlib
import datetime
from abc import ABC, abstractmethod


# ============================================================
# Custom Exceptions
# ============================================================

class InsufficientFundsError(Exception):
    """Raised when withdrawal exceeds available balance."""
    pass

class InvalidAmountError(Exception):
    """Raised when a non-positive amount is entered."""
    pass

class AuthenticationError(Exception):
    """Raised when PIN verification fails."""
    pass

class AccountNotFoundError(Exception):
    """Raised when account number doesn't exist in the bank."""
    pass


# ============================================================
# Abstract Base Class — BankAccount
# ============================================================

class BankAccount(ABC):
    """
    Abstract base class for all bank account types.
    Implements Encapsulation + File Handling.
    Subclasses must implement: apply_interest(), account_type
    """

    TRANSACTION_FILE = "transactions.csv"

    def __init__(self, account_holder: str, account_number: str, initial_balance: float = 0.0):
        self.__account_holder = account_holder
        self.__account_number = account_number
        self.__balance = initial_balance
        self.__pin_hash = None
        self.__transaction_history = []
        self.__is_active = True

        # Initialize CSV file with headers if it doesn't exist
        self._init_csv()
        self._log_transaction("ACCOUNT OPENED", initial_balance)

    # ---- Abstract Methods (must override in subclasses) ----

    @property
    @abstractmethod
    def account_type(self) -> str:
        pass

    @abstractmethod
    def apply_interest(self) -> str:
        pass

    # ---- Getters ----

    def get_account_holder(self) -> str:
        return self.__account_holder

    def get_account_number(self) -> str:
        return self.__account_number

    def get_masked_number(self) -> str:
        n = self.__account_number
        return "*" * (len(n) - 4) + n[-4:]

    def get_balance(self) -> float:
        return self.__balance

    def is_active(self) -> bool:
        return self.__is_active

    # ---- PIN Management ----

    def set_pin(self, pin: str) -> None:
        if not pin.isdigit() or len(pin) != 4:
            raise ValueError("PIN must be exactly 4 numeric digits.")
        self.__pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        print("✅ PIN set successfully.")

    def verify_pin(self, pin: str) -> bool:
        entered_hash = hashlib.sha256(pin.encode()).hexdigest()
        return self.__pin_hash == entered_hash

    # ---- Core Operations ----

    def deposit(self, amount: float) -> str:
        self._validate_amount(amount)
        self.__balance += amount
        self._log_transaction("DEPOSIT", amount)
        return f"✅ Deposited ₹{amount:,.2f} | New Balance: ₹{self.__balance:,.2f}"

    def withdraw(self, amount: float) -> str:
        self._validate_amount(amount)
        if amount > self.__balance:
            raise InsufficientFundsError(
                f"❌ Insufficient funds. Available: ₹{self.__balance:,.2f}"
            )
        self.__balance -= amount
        self._log_transaction("WITHDRAWAL", amount)
        return f"✅ Withdrawn ₹{amount:,.2f} | New Balance: ₹{self.__balance:,.2f}"

    def transfer(self, target_account: "BankAccount", amount: float) -> str:
        self._validate_amount(amount)
        if amount > self.__balance:
            raise InsufficientFundsError(
                f"❌ Insufficient funds for transfer. Available: ₹{self.__balance:,.2f}"
            )
        self.__balance -= amount
        target_account._credit(amount)
        self._log_transaction(f"TRANSFER TO {target_account.get_masked_number()}", amount)
        target_account._log_transaction(f"TRANSFER FROM {self.get_masked_number()}", amount)
        return (f"✅ Transferred ₹{amount:,.2f} to {target_account.get_account_holder()}\n"
                f"   Your Balance: ₹{self.__balance:,.2f}")

    def _credit(self, amount: float) -> None:
        """Internal method: directly credit balance (used during transfer)."""
        self.__balance += amount

    def check_balance(self) -> str:
        return (f"\n💰 Account Balance\n"
                f"   Holder : {self.__account_holder}\n"
                f"   Type   : {self.account_type}\n"
                f"   Account: {self.get_masked_number()}\n"
                f"   Balance: ₹{self.__balance:,.2f}")

    def mini_statement(self) -> str:
        if not self.__transaction_history:
            return "No transactions found."
        recent = self.__transaction_history[-5:]
        lines = [f"\n📋 Mini Statement — Last {len(recent)} Transactions",
                 "-" * 60]
        for t in recent:
            lines.append(t)
        lines.append("-" * 60)
        return "\n".join(lines)

    def deactivate(self) -> None:
        self.__is_active = False
        self._log_transaction("ACCOUNT DEACTIVATED", 0)

    # ---- File Handling ----

    def _init_csv(self) -> None:
        """Create the CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.TRANSACTION_FILE):
            with open(self.TRANSACTION_FILE, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Account No", "Holder", "Type", "Transaction", "Amount (₹)", "Balance (₹)"])

    def _log_transaction(self, txn_type: str, amount: float) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {txn_type:<30} ₹{amount:>10,.2f}  |  Bal: ₹{self.__balance:,.2f}"
        self.__transaction_history.append(entry)
        self._save_to_csv(timestamp, txn_type, amount)

    def _save_to_csv(self, timestamp: str, txn_type: str, amount: float) -> None:
        try:
            with open(self.TRANSACTION_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp,
                    self.__account_number,
                    self.__account_holder,
                    self.account_type,
                    txn_type,
                    f"{amount:.2f}",
                    f"{self.__balance:.2f}"
                ])
        except IOError as e:
            print(f"⚠️  File error: {e}")

    def load_full_history(self) -> str:
        """Read this account's full history from the CSV file."""
        if not os.path.exists(self.TRANSACTION_FILE):
            return "No transaction file found."
        try:
            lines = [f"\n📂 Full Transaction History — {self.__account_holder}",
                     "-" * 80,
                     f"{'Date & Time':<22} {'Type':<30} {'Amount':>12} {'Balance':>12}",
                     "-" * 80]
            with open(self.TRANSACTION_FILE, "r") as f:
                reader = csv.DictReader(f)
                found = False
                for row in reader:
                    if row["Account No"] == self.__account_number:
                        found = True
                        lines.append(
                            f"{row['Timestamp']:<22} {row['Transaction']:<30} "
                            f"₹{float(row['Amount (₹)']):>10,.2f}  ₹{float(row['Balance (₹)']):>10,.2f}"
                        )
            if not found:
                return "No records found for this account."
            lines.append("-" * 80)
            return "\n".join(lines)
        except IOError as e:
            return f"⚠️  File read error: {e}"

    # ---- Validation ----

    @staticmethod
    def _validate_amount(amount: float) -> None:
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise InvalidAmountError("❌ Amount must be a positive number.")


# ============================================================
# Subclass 1 — Savings Account (Inheritance)
# ============================================================

class SavingsAccount(BankAccount):
    """
    Savings Account with 4% annual interest.
    Minimum balance: ₹1000
    """

    INTEREST_RATE = 0.04
    MIN_BALANCE = 1000.0

    def __init__(self, account_holder: str, account_number: str, initial_balance: float = 1000.0):
        if initial_balance < self.MIN_BALANCE:
            raise ValueError(f"Savings account requires minimum ₹{self.MIN_BALANCE:,.2f} to open.")
        super().__init__(account_holder, account_number, initial_balance)

    @property
    def account_type(self) -> str:
        return "Savings Account"

    def apply_interest(self) -> str:
        interest = round(self.get_balance() * self.INTEREST_RATE, 2)
        result = self.deposit(interest)
        return f"🏦 Interest Applied @ 4% p.a. | +₹{interest:,.2f}\n{result}"

    def withdraw(self, amount: float) -> str:
        """Override to enforce minimum balance rule."""
        self._validate_amount(amount)
        if self.get_balance() - amount < self.MIN_BALANCE:
            raise InsufficientFundsError(
                f"❌ Cannot withdraw. Minimum balance of ₹{self.MIN_BALANCE:,.2f} must be maintained."
            )
        return super().withdraw(amount)


# ============================================================
# Subclass 2 — Current Account (Inheritance)
# ============================================================

class CurrentAccount(BankAccount):
    """
    Current Account with overdraft facility up to ₹10,000.
    No interest. Suitable for businesses.
    """

    OVERDRAFT_LIMIT = 10000.0

    def __init__(self, account_holder: str, account_number: str, initial_balance: float = 0.0):
        super().__init__(account_holder, account_number, initial_balance)

    @property
    def account_type(self) -> str:
        return "Current Account"

    def apply_interest(self) -> str:
        return "ℹ️  Current accounts do not earn interest."

    def withdraw(self, amount: float) -> str:
        """Override to allow overdraft."""
        self._validate_amount(amount)
        if amount > self.get_balance() + self.OVERDRAFT_LIMIT:
            raise InsufficientFundsError(
                f"❌ Exceeds overdraft limit. Max withdrawable: ₹{self.get_balance() + self.OVERDRAFT_LIMIT:,.2f}"
            )
        return super().withdraw(amount)


# ============================================================
# Bank Class — Manages Multiple Accounts
# ============================================================

class Bank:
    """Central bank that manages multiple accounts."""

    def __init__(self, name: str):
        self.__name = name
        self.__accounts: dict[str, BankAccount] = {}

    def get_name(self) -> str:
        return self.__name

    def add_account(self, account: BankAccount) -> None:
        self.__accounts[account.get_account_number()] = account
        print(f"✅ Account added: {account.get_account_holder()} ({account.account_type})")

    def get_account(self, account_number: str) -> BankAccount:
        if account_number not in self.__accounts:
            raise AccountNotFoundError(f"❌ Account '{account_number}' not found.")
        return self.__accounts[account_number]

    def list_accounts(self) -> None:
        print(f"\n🏦 {self.__name} — Registered Accounts")
        print("-" * 45)
        for acc in self.__accounts.values():
            status = "Active" if acc.is_active() else "Inactive"
            print(f"  {acc.get_masked_number()} | {acc.account_type:<20} | {acc.get_account_holder()} | {status}")
        print("-" * 45)


# ============================================================
# ATM Class — User Interface
# ============================================================

class ATM:
    """ATM machine: handles authentication and banking operations."""

    MAX_ATTEMPTS = 3

    def __init__(self, bank: Bank):
        self.__bank = bank
        self.__current_account: BankAccount = None

    def start(self) -> None:
        print(f"\n{'='*45}")
        print(f"   🏧 Welcome to {self.__bank.get_name()} ATM")
        print(f"{'='*45}")

        account_number = input("Enter Account Number: ").strip()
        try:
            account = self.__bank.get_account(account_number)
        except AccountNotFoundError as e:
            print(e)
            return

        if not account.is_active():
            print("❌ This account is deactivated. Contact your bank.")
            return

        if self._authenticate(account):
            self.__current_account = account
            self._menu()

    def _authenticate(self, account: BankAccount) -> bool:
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            pin = input(f"Enter PIN (Attempt {attempt}/{self.MAX_ATTEMPTS}): ").strip()
            if account.verify_pin(pin):
                print(f"\n✅ Authenticated! Welcome, {account.get_account_holder()}.")
                return True
            print("❌ Incorrect PIN.")
        print("🔒 Account locked. Contact your bank.")
        return False

    def _menu(self) -> None:
        acc = self.__current_account
        while True:
            print(f"\n{'='*40}")
            print(f"  {acc.account_type} | {acc.get_masked_number()}")
            print(f"{'='*40}")
            print("  1. Check Balance")
            print("  2. Deposit")
            print("  3. Withdraw")
            print("  4. Transfer Funds")
            print("  5. Apply Interest")
            print("  6. Mini Statement")
            print("  7. Full History (CSV)")
            print("  8. Exit")
            print(f"{'='*40}")

            choice = input("Select (1-8): ").strip()

            try:
                if choice == "1":
                    print(acc.check_balance())

                elif choice == "2":
                    amt = float(input("Deposit Amount ₹: "))
                    print(acc.deposit(amt))

                elif choice == "3":
                    amt = float(input("Withdrawal Amount ₹: "))
                    print(acc.withdraw(amt))

                elif choice == "4":
                    target_no = input("Enter target account number: ").strip()
                    target = self.__bank.get_account(target_no)
                    amt = float(input("Transfer Amount ₹: "))
                    print(acc.transfer(target, amt))

                elif choice == "5":
                    print(acc.apply_interest())

                elif choice == "6":
                    print(acc.mini_statement())

                elif choice == "7":
                    print(acc.load_full_history())

                elif choice == "8":
                    print(f"\n👋 Thank you, {acc.get_account_holder()}. Goodbye!")
                    break

                else:
                    print("❌ Invalid option.")

            except (InsufficientFundsError, InvalidAmountError, AccountNotFoundError) as e:
                print(e)
            except ValueError:
                print("❌ Please enter a valid numeric amount.")


# ============================================================
# Main
# ============================================================

def main():
    # Setup bank
    bank = Bank("PyBank")

    # Create accounts
    savings = SavingsAccount("Rahul Sharma", "SAV001", initial_balance=5000.0)
    savings.set_pin("1234")

    current = CurrentAccount("Priya Mehta", "CUR002", initial_balance=10000.0)
    current.set_pin("5678")

    # Register accounts with bank
    bank.add_account(savings)
    bank.add_account(current)

    bank.list_accounts()

    # Start ATM session
    atm = ATM(bank)
    atm.start()


if __name__ == "__main__":
    main()
