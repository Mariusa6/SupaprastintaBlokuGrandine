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


class MerkleTree:
    """
    Tikras Merkle Tree
    """
    
    def __init__(self, transactions: List[Transaction]):
        self.transactions = transactions
        self.tree = []  # Visi lygiai
        self.root = self._build_tree()
    
    def _build_tree(self) -> str:
        """Stato Merkle Tree lygis po lygio"""
        if not self.transactions:
            return hashlib.sha256("".encode()).hexdigest()
        
        # Pradinis lygis - transakcijų hash'ai
        current_level = [tx.transaction_id for tx in self.transactions]
        self.tree.append(current_level.copy())
        
        print(f"\nStatomas Merkle Tree:")
        print(f"  Level 0: {len(current_level)} hash(es)")
        
        # Statome medį aukštyn
        level = 1
        while len(current_level) > 1:
            next_level = []
            
            # Jei nelyginis - dubliuojame paskutinį
            if len(current_level) % 2 != 0:
                current_level.append(current_level[-1])
                print(f"    Nelyginis skaičius - dubliuojame paskutinį")
            
            # Poruojame ir hash'uojame
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1]
                combined = left + right
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(parent_hash)
            
            self.tree.append(next_level.copy())
            print(f"  Level {level}: {len(next_level)} hash(es)")
            
            current_level = next_level
            level += 1
        
        print(f"  Root: {current_level[0][:32]}...")
        return current_level[0]
    
    def get_root(self) -> str:
        """Grąžina Merkle Root hash"""
        return self.root
    
    def __repr__(self):
        return f"MerkleTree(root={self.root[:16]}..., levels={len(self.tree)})"


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
    """Bloko klasė - dabar su tikru Merkle Tree"""
    
    def __init__(self, prev_block_hash: str, transactions: List[Transaction],
                 version: str = "1.0", difficulty_target: int = 3):
        self.version = version
        self.timestamp = time.time()
        self.prev_block_hash = prev_block_hash
        self.transactions = transactions
        self.difficulty_target = difficulty_target
        self.nonce = 0
        
        # Dabar naudojame tikrą MerkleTree!
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
        start_time = time.time()
        
        print(f"\nKasimas (target: {target}...)")
        
        while True:
            self.block_hash = self.calculate_hash()
            attempts += 1
            
            if self.block_hash.startswith(target):
                elapsed = time.time() - start_time
                print(f"  Iškasta! Nonce: {self.nonce}, "
                      f"Bandymų: {attempts}, Laikas: {elapsed:.2f}s")
                return True
            
            self.nonce += 1
    
    def __repr__(self):
        return f"Block(hash={self.block_hash[:16]}..., tx={len(self.transactions)})"


# Testavimas
if __name__ == "__main__":
    print("="*70)
    print("Tikras Merkle Tree")
    print("="*70)
    
    # Sukuriame transakcijas
    transactions = [
        Transaction("alice", "bob", 10.0),
        Transaction("bob", "charlie", 20.0),
        Transaction("charlie", "diana", 30.0),
        Transaction("diana", "alice", 40.0),
    ]
    
    print("\nTransakcijos:")
    for i, tx in enumerate(transactions):
        print(f"  TX{i+1}: {tx.transaction_id[:16]}...")
    
    # Sukuriame tikrą Merkle Tree
    merkle = MerkleTree(transactions)
    
    print(f"\nMerkle Tree Info:")
    print(f"  {merkle}")
    print(f"  Lygių: {len(merkle.tree)}")
    
    # Rodom kiekvieną lygį
    print(f"\nVisi Merkle Tree lygiai:")
    for level, hashes in enumerate(merkle.tree):
        print(f"\n  Level {level}:")
        for i, h in enumerate(hashes):
            print(f"    [{i}] {h[:32]}...")
    
    print(f"\nMerkle Root: {merkle.root}")
    
    # Sukuriame bloką su tikru Merkle Tree
    print(f"\n" + "="*70)
    print("Blokas su tikru Merkle Tree")
    print("="*70)
    
    block = Block(
        prev_block_hash="0"*64,
        transactions=transactions,
        difficulty_target=2
    )
    
    print(f"\n  Bloko Merkle root: {block.merkle_root}")
    print(f"  Tree Merkle root:  {merkle.root}")
    print(f"  Sutampa: {block.merkle_root == merkle.root}")
    
    # Kasame bloką
    block.mine_block()
