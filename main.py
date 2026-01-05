import hashlib
import time
from datetime import datetime
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
    """Bloko klasė"""
    
    def __init__(self, prev_block_hash: str, transactions: List[Transaction],
                 version: str = "1.0", difficulty_target: int = 3):
        self.version = version
        self.timestamp = time.time()
        self.prev_block_hash = prev_block_hash
        self.transactions = transactions
        self.difficulty_target = difficulty_target
        self.nonce = 0
        self.merkle_tree = SimpleMerkleTree(transactions)
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
                print(f"Blokas iškastas! Nonce: {self.nonce}, Bandymų: {attempts}")
                return True
            
            self.nonce += 1
    
    def __repr__(self):
        return f"Block(hash={self.block_hash[:16]}..., tx={len(self.transactions)})"


class Blockchain:

    def __init__(self, difficulty: int = 3):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.users: Dict[str, User] = {}
        self.pending_transactions: List[Transaction] = []
        
        # Sukuriame Genesis bloką
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        print("\nKuriamas Genesis blokas...")
        
        genesis_block = Block(
            prev_block_hash="0" * 64,
            transactions=[],
            difficulty_target=self.difficulty
        )
        
        genesis_block.block_hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)
        
        print(f"Genesis blokas sukurtas!")
        print(f"  Hash: {genesis_block.block_hash[:32]}...")
    
    def get_last_block(self) -> Block:
        """Grąžina paskutinį bloką"""
        return self.chain[-1]
    
    def add_user(self, user: User):
        """Prideda vartotoją"""
        self.users[user.public_key] = user
    
    def add_transaction(self, transaction: Transaction):
        """Prideda transakciją"""
        self.pending_transactions.append(transaction)
    
    def is_chain_valid(self) -> bool:
        """Validuoja grandinę"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            # Tikrina hash
            if current.block_hash != current.calculate_hash():
                return False
            
            # Tikrina sąsają
            if current.prev_block_hash != previous.block_hash:
                return False
            
            # Tikrina difficulty
            if not current.block_hash.startswith("0" * current.difficulty_target):
                return False
        
        return True
    
    def print_chain(self):
        """Išveda grandinę"""
        print("\nBLOKŲ GRANDINĖ")
        print("="*50)
        
        for i, block in enumerate(self.chain):
            print(f"\nBlokas #{i}")
            print(f"  Hash: {block.block_hash[:32]}...")
            print(f"  Prev: {block.prev_block_hash[:32]}...")
            print(f"  TX: {len(block.transactions)}")
            print(f"  Nonce: {block.nonce}")
        
        print(f"\nGrandinė valid: {self.is_chain_valid()}")
    
    def __repr__(self):
        return f"Blockchain(blocks={len(self.chain)}, pending_tx={len(self.pending_transactions)})"


# Testavimas
if __name__ == "__main__":
    print("Blockchain klasė")
    print("="*50)
    
    # Sukuriame blockchain
    blockchain = Blockchain(difficulty=2)
    
    # Pridedame vartotojus
    user1 = User("Alice", "key_alice", 1000.0)
    user2 = User("Bob", "key_bob", 500.0)
    
    blockchain.add_user(user1)
    blockchain.add_user(user2)
    
    print(f"\nPridėta vartotojų: {len(blockchain.users)}")
    
    # Pridedame transakcijas
    tx1 = Transaction(user1.public_key, user2.public_key, 100.0)
    tx2 = Transaction(user2.public_key, user1.public_key, 50.0)
    
    blockchain.add_transaction(tx1)
    blockchain.add_transaction(tx2)
    
    print(f"Pridėta transakcijų: {len(blockchain.pending_transactions)}")
    
    # Rodom blockchain
    print(f"\n{blockchain}")
    blockchain.print_chain()