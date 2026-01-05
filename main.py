import hashlib
import time
from typing import List


class User:
    """Vartotojo klasė"""
    
    def __init__(self, name: str, public_key: str, balance: float):
        self.name = name
        self.public_key = public_key
        self.balance = balance
    
    def __repr__(self):
        return f"User({self.name}, {self.balance:.2f})"


class Transaction:
    """Transakcijos klasė"""
    
    def __init__(self, sender: str, receiver: str, amount: float):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.transaction_id = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        data = f"{self.sender}{self.receiver}{self.amount}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def __repr__(self):
        return f"TX({self.sender[:8]}→{self.receiver[:8]}: {self.amount:.2f})"


class SimpleMerkleTree:
    """Supaprastinta Merkle Tree"""
    
    def __init__(self, transactions: List[Transaction]):
        self.transactions = transactions
        self.root = self._calculate_simple_hash()
    
    def _calculate_simple_hash(self) -> str:
        if not self.transactions:
            return hashlib.sha256("".encode()).hexdigest()
        all_tx_ids = ''.join([tx.transaction_id for tx in self.transactions])
        return hashlib.sha256(all_tx_ids.encode()).hexdigest()
    
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
    def __init__(self, prev_block_hash: str, transactions: List[Transaction],
                 version: str = "1.0", difficulty_target: int = 3):
        self.version = version
        self.timestamp = time.time()
        self.prev_block_hash = prev_block_hash
        self.transactions = transactions
        self.difficulty_target = difficulty_target
        self.nonce = 0
        
        # Sukuriame Merkle Tree
        self.merkle_tree = SimpleMerkleTree(transactions)
        self.merkle_root = self.merkle_tree.get_root()
        
        # Bloko hash
        self.block_hash = ""
    
    def calculate_hash(self) -> str:
        """Apskaičiuoja bloko hash"""
        header_data = (
            f"{self.prev_block_hash}"
            f"{self.timestamp}"
            f"{self.version}"
            f"{self.merkle_root}"
            f"{self.nonce}"
            f"{self.difficulty_target}"
        )
        return hashlib.sha256(header_data.encode()).hexdigest()
    
    def mine_block(self) -> bool:
        target = "0" * self.difficulty_target
        attempts = 0
        start_time = time.time()
        
        print(f"\nKasimas pradėtas (target: {target}...)")
        
        while True:
            self.block_hash = self.calculate_hash()
            attempts += 1
            
            # Rodome progresą
            if attempts % 10000 == 0:
                elapsed = time.time() - start_time
                print(f"  Bandymas #{attempts}, laikas: {elapsed:.2f}s")
            
            # Tikriname ar hash atitinka target
            if self.block_hash.startswith(target):
                elapsed = time.time() - start_time
                print(f"  Blokas iškastas!")
                print(f"  Hash: {self.block_hash}")
                print(f"  Nonce: {self.nonce}")
                print(f"  Bandymų: {attempts}")
                print(f"  Laikas: {elapsed:.2f}s")
                return True
            
            self.nonce += 1
    
    def __repr__(self):
        return f"Block(hash={self.block_hash[:16]}..., tx={len(self.transactions)})"


# Testavimas
if __name__ == "__main__":
    print("="*50)
    
    # Sukuriame transakcijas
    tx1 = Transaction("alice_key", "bob_key", 50.0)
    tx2 = Transaction("bob_key", "charlie_key", 25.0)
    
    print("\nTransakcijos:")
    print(f"  {tx1}")
    print(f"  {tx2}")
    
    # Sukuriame bloką
    block = Block(
        prev_block_hash="0"*64,
        transactions=[tx1, tx2],
        difficulty_target=2  # Lengvesnis difficulty testavimui
    )
    
    print(f"\nBlokas sukurtas")
    print(f"  Merkle root: {block.merkle_root[:32]}...")
    
    # Kasame bloką
    block.mine_block()
    
    print(f"\nGalutinis blokas:")
    print(f"  {block}")
