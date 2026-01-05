import hashlib
import time
from typing import List, Dict


class User:
    """Vartotojo klasė"""
    
    def __init__(self, name: str, public_key: str, balance: float):
        self.name = name
        self.public_key = public_key
        self.balance = balance
    
    def __repr__(self):
        return f"User({self.name}, {self.balance:.2f})"


class Transaction:
    """Transakcijos klasė - dabar su validacija!"""
    
    def __init__(self, sender: str, receiver: str, amount: float):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.transaction_id = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        data = f"{self.sender}{self.receiver}{self.amount}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def is_valid(self, users_dict: Dict[str, User]) -> bool:
        """
        Transakcijos validacija
        """
        # 1. Tikrina ar siuntėjas egzistuoja
        if self.sender not in users_dict:
            print(f"  Siuntėjas {self.sender[:8]}... neegzistuoja")
            return False
        
        # 2. Tikrina ar gavėjas egzistuoja
        if self.receiver not in users_dict:
            print(f"  Gavėjas {self.receiver[:8]}... neegzistuoja")
            return False
        
        # 3. Tikrina ar suma teigiama
        if self.amount <= 0:
            print(f"  Suma {self.amount} nėra teigiama")
            return False
        
        # 4. Tikrina ar siuntėjas turi pakankamai lėšų
        if users_dict[self.sender].balance < self.amount:
            sender_balance = users_dict[self.sender].balance
            print(f"  Nepakanka lėšų: turi {sender_balance:.2f}, "
                  f"reikia {self.amount:.2f}")
            return False
        
        # 5. Tikrina ar transaction_id teisingas
        expected_hash = hashlib.sha256(
            f"{self.sender}{self.receiver}{self.amount}".encode()
        ).hexdigest()
        
        if self.transaction_id != expected_hash:
            print(f"  Transaction ID neteisingas")
            return False
        
        return True
    
    def __repr__(self):
        return f"TX({self.sender[:8]}→{self.receiver[:8]}: {self.amount:.2f})"


class MerkleTree:
    """Tikras Merkle Tree"""
    
    def __init__(self, transactions: List[Transaction]):
        self.transactions = transactions
        self.tree = []
        self.root = self._build_tree()
    
    def _build_tree(self) -> str:
        if not self.transactions:
            return hashlib.sha256("".encode()).hexdigest()
        
        current_level = [tx.transaction_id for tx in self.transactions]
        self.tree.append(current_level.copy())
        
        while len(current_level) > 1:
            next_level = []
            
            if len(current_level) % 2 != 0:
                current_level.append(current_level[-1])
            
            for i in range(0, len(current_level), 2):
                combined = current_level[i] + current_level[i + 1]
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(parent_hash)
            
            self.tree.append(next_level.copy())
            current_level = next_level
        
        return current_level[0]
    
    def get_root(self) -> str:
        return self.root


class BlockHeader:
    """Bloko antraštės klasė"""
    
    def __init__(self, prev_block_hash: str, timestamp: float, version: str,
                 merkle_root: str, nonce: int, difficulty_target: int):
        self.prev_block_hash = prev_block_hash
        self.timestamp = timestamp
        self.version = version
        self.merkle_root = merkle_root
        self.nonce = nonce
        self.difficulty_target = difficulty_target


class Block:
    """Bloko klasė"""
    
    def __init__(self, prev_block_hash: str, transactions: List[Transaction],
                 version: str = "1.0", difficulty_target: int = 3):
        self.version = version
        self.timestamp = time.time()
        self.prev_block_hash = prev_block_hash
        self.transactions = transactions
        self.difficulty_target = difficulty_target
        self.nonce = 0
        self.merkle_tree = MerkleTree(transactions)
        self.merkle_root = self.merkle_tree.get_root()
        self.block_hash = ""
    
    def calculate_hash(self) -> str:
        header_data = (
            f"{self.prev_block_hash}{self.timestamp}{self.version}"
            f"{self.merkle_root}{self.nonce}{self.difficulty_target}"
        )
        return hashlib.sha256(header_data.encode()).hexdigest()
    
    def mine_block(self) -> bool:
        target = "0" * self.difficulty_target
        attempts = 0
        
        while True:
            self.block_hash = self.calculate_hash()
            attempts += 1
            
            if self.block_hash.startswith(target):
                print(f"  Iškasta! Nonce: {self.nonce}, Bandymų: {attempts}")
                return True
            
            self.nonce += 1


# Testavimas
if __name__ == "__main__":
    print("="*70)
    print("Transakcijų validacija")
    print("="*70)
    
    # Sukuriame vartotojus
    users = {
        "key_alice": User("Alice", "key_alice", 1000.0),
        "key_bob": User("Bob", "key_bob", 500.0),
        "key_charlie": User("Charlie", "key_charlie", 100.0),
    }
    
    print("\nVartotojai:")
    for key, user in users.items():
        print(f"  {user}")
    
    # Testuojame validacijas
    print("\n" + "="*70)
    print("TRANSAKCIJŲ VALIDACIJOS TESTAI")
    print("="*70)
    
    # Test 1: Valid transakcija
    print("\nValid transakcija:")
    tx1 = Transaction("key_alice", "key_bob", 100.0)
    print(f"  {tx1}")
    result = tx1.is_valid(users)
    print(f"  Validacija: {result}")
    
    # Test 2: Per didelė suma
    print("\nPer didelė suma (Charlie turi tik 100):")
    tx2 = Transaction("key_charlie", "key_alice", 200.0)
    print(f"  {tx2}")
    result = tx2.is_valid(users)
    print(f"  Validacija: {result}")
    
    # Test 3: Neigiama suma
    print("\nNeigiama suma:")
    tx3 = Transaction("key_alice", "key_bob", -50.0)
    print(f"  {tx3}")
    result = tx3.is_valid(users)
    print(f"  Validacija: {result}")
    
    # Test 4: Neegzistuojantis siuntėjas
    print("\nNeegzistuojantis siuntėjas:")
    tx4 = Transaction("key_unknown", "key_bob", 50.0)
    print(f"  {tx4}")
    result = tx4.is_valid(users)
    print(f"  Validacija: {result}")
    
    # Test 5: Kelios valid transakcijos
    print("\nKelios valid transakcijos:")
    valid_txs = []
    test_txs = [
        Transaction("key_alice", "key_bob", 50.0),
        Transaction("key_bob", "key_charlie", 30.0),
        Transaction("key_charlie", "key_alice", 20.0),
        Transaction("key_alice", "key_charlie", 2000.0),  # Invalid - per daug
    ]
    
    for tx in test_txs:
        if tx.is_valid(users):
            valid_txs.append(tx)
            print(f"  validžios{tx}")
        else:
            print(f" nevalidžios {tx}")
    
    print(f"\n  Valid transakcijų: {len(valid_txs)}/{len(test_txs)}")
    
    # Sukuriame bloką su valid transakcijomis
    print("\n" + "="*70)
    print("Blokas su tik VALID transakcijomis")
    print("="*70)
    
    block = Block(
        prev_block_hash="0"*64,
        transactions=valid_txs,
        difficulty_target=2
    )
    
    print(f"\n  Transakcijų bloke: {len(block.transactions)}")
    print(f"  Merkle root: {block.merkle_root[:32]}...")
    
    block.mine_block()
