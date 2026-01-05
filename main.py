import hashlib
from typing import List


class User:
    """Vartotojo klasė su vardu, viešuoju raktu ir balansu"""
    
    def __init__(self, name: str, public_key: str, balance: float):
        self.name = name
        self.public_key = public_key
        self.balance = balance
    
    def __repr__(self):
        return f"User(name={self.name}, key={self.public_key[:8]}..., balance={self.balance:.2f})"


class Transaction:
    """Transakcijos klasė"""
    
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


class SimpleMerkleTree:
    def __init__(self, transactions: List[Transaction]):
        self.transactions = transactions
        self.root = self._calculate_simple_hash()
    
    def _calculate_simple_hash(self) -> str:
        """Paprastas visų transakcijų ID hash"""
        if not self.transactions:
            return hashlib.sha256("".encode()).hexdigest()
        
        # Sujungiame visus transaction ID ir hash'uojame
        all_tx_ids = ''.join([tx.transaction_id for tx in self.transactions])
        return hashlib.sha256(all_tx_ids.encode()).hexdigest()
    
    def get_root(self) -> str:
        """Grąžina 'Merkle' root hash"""
        return self.root
    
    def __repr__(self):
        return f"SimpleMerkleTree(root={self.root[:16]}..., tx_count={len(self.transactions)})"


class BlockHeader:
    def __init__(self, prev_block_hash: str, timestamp: float, version: str,
                 merkle_root: str, nonce: int, difficulty_target: int):
        self.prev_block_hash = prev_block_hash
        self.timestamp = timestamp
        self.version = version
        self.merkle_root = merkle_root
        self.nonce = nonce
        self.difficulty_target = difficulty_target
    
    def __repr__(self):
        return f"BlockHeader(prev={self.prev_block_hash[:16]}..., nonce={self.nonce})"


# Testavimas
if __name__ == "__main__":
    print("="*50)
    
    # Sukuriame transakcijas
    tx1 = Transaction("sender1", "receiver1", 10.0)
    tx2 = Transaction("sender2", "receiver2", 20.0)
    tx3 = Transaction("sender3", "receiver3", 30.0)
    
    print("\nTransakcijos:")
    print(f"  {tx1}")
    print(f"  {tx2}")
    print(f"  {tx3}")
    
    # Sukuriame SimpleMerkleTree
    merkle = SimpleMerkleTree([tx1, tx2, tx3])
    
    print("\nSimpleMerkleTree:")
    print(f"  {merkle}")
    print(f"  Root: {merkle.root}")
    
    # Sukuriame BlockHeader
    import time
    header = BlockHeader(
        prev_block_hash="0"*64,
        timestamp=time.time(),
        version="1.0",
        merkle_root=merkle.root,
        nonce=0,
        difficulty_target=3
    )
    
    print("\nBlockHeader:")
    print(f"  {header}")