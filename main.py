import hashlib


class User:
    """Vartotojo klasė su vardu, viešuoju raktu ir balansu"""
    
    def __init__(self, name: str, public_key: str, balance: float):
        self.name = name
        self.public_key = public_key
        self.balance = balance
    
    def __repr__(self):
        return f"User(name={self.name}, key={self.public_key[:8]}..., balance={self.balance:.2f})"


class Transaction:
    """Transakcijos klasė - bazinė versija"""
    
    def __init__(self, sender: str, receiver: str, amount: float):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.transaction_id = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Apskaičiuoja transakcijos hash"""
        data = f"{self.sender}{self.receiver}{self.amount}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def __repr__(self):
        return f"TX({self.sender[:8]}→{self.receiver[:8]}: {self.amount:.2f})"


# Testavimas
if __name__ == "__main__":
    print("User ir Transaction klasės")
    print("="*50)
    
    # Testuojame User
    user1 = User("Alice", "abc123def456", 1000.0)
    user2 = User("Bob", "xyz789uvw012", 500.0)
    
    print("\nVartotojai:")
    print(f"  {user1}")
    print(f"  {user2}")
    
    # Testuojame Transaction
    tx = Transaction(user1.public_key, user2.public_key, 100.0)
    
    print("\nTransakcija:")
    print(f"  {tx}")
    print(f"  TX ID: {tx.transaction_id[:32]}...")
