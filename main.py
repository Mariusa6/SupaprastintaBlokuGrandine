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
    """Supaprastinta Merkle Tree - v0.1"""
    
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
        start_time = time.time()
        
        while True:
            self.block_hash = self.calculate_hash()
            attempts += 1
            
            if self.block_hash.startswith(target):
                elapsed = time.time() - start_time
                print(f"  Iškasta! Nonce: {self.nonce}, Bandymų: {attempts}, "
                      f"Laikas: {elapsed:.2f}s")
                return True
            
            self.nonce += 1
    
    def __repr__(self):
        return f"Block(#{self.block_hash[:8]}..., tx={len(self.transactions)})"


class Blockchain:
    """Blokų grandinės klasė - v0.1 CENTRALIZUOTA"""
    
    def __init__(self, difficulty: int = 3):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.users: Dict[str, User] = {}
        self.pending_transactions: List[Transaction] = []
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """Genesis bloko kūrimas"""
        print("\nKuriamas Genesis blokas...")
        genesis_block = Block(
            prev_block_hash="0" * 64,
            transactions=[],
            difficulty_target=self.difficulty
        )
        genesis_block.block_hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)
        print(f"  Genesis: {genesis_block.block_hash[:32]}...")
    
    def get_last_block(self) -> Block:
        return self.chain[-1]
    
    def add_user(self, user: User):
        self.users[user.public_key] = user
    
    def add_transaction(self, transaction: Transaction):
        self.pending_transactions.append(transaction)
    
    def mine_pending_transactions(self, transactions_per_block: int = 100) -> bool:
        """
        Kasa bloką su pending transakcijomis
        Centralizuotas - tiesiog ima pirmas N transakcijų ir kasa
        """
        if len(self.pending_transactions) < transactions_per_block:
            print(f"Per mažai TX: {len(self.pending_transactions)}")
            return False
        
        # Pasirenkame transakcijas
        selected_txs = self.pending_transactions[:transactions_per_block]
        
        print(f"\nKasomas blokas #{len(self.chain)}")
        print(f"  TX: {len(selected_txs)}")
        
        # Sukuriame bloką
        new_block = Block(
            prev_block_hash=self.get_last_block().block_hash,
            transactions=selected_txs,
            difficulty_target=self.difficulty
        )
        
        # Kasame
        success = new_block.mine_block()
        
        if success:
            #Atnaujiname balansus
            for tx in selected_txs:
                if tx.sender in self.users and tx.receiver in self.users:
                    self.users[tx.sender].balance -= tx.amount
                    self.users[tx.receiver].balance += tx.amount
            
            # Pašaliname transakcijas
            self.pending_transactions = self.pending_transactions[transactions_per_block:]
            
            # Pridedame bloką
            self.chain.append(new_block)
            
            print(f"  Blokas #{len(self.chain)-1} pridėtas!")
            print(f"  Liko TX: {len(self.pending_transactions)}")
            
            return True
        
        return False
    
    def is_chain_valid(self) -> bool:
        """Validuoja grandinę"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            if current.block_hash != current.calculate_hash():
                return False
            if current.prev_block_hash != previous.block_hash:
                return False
            if not current.block_hash.startswith("0" * current.difficulty_target):
                return False
        
        return True
    
    def print_chain(self):
        """Išveda grandinę"""
        print("\n" + "="*60)
        print("BLOKŲ GRANDINĖ (v0.1)")
        print("="*60)
        
        for i, block in enumerate(self.chain):
            print(f"\n Blokas #{i}")
            print(f"  Hash: {block.block_hash}")
            print(f"  Prev: {block.prev_block_hash[:32]}...")
            print(f"  TX: {len(block.transactions)}")
            print(f"  Timestamp: {datetime.fromtimestamp(block.timestamp)}")
        
        print(f"\n{'='*60}")
        print(f"Blokų: {len(self.chain)}")
        print(f"Grandinė valid: {self.is_chain_valid()}")
        print(f"{'='*60}")
    
    def get_statistics(self):
        """Statistika"""
        total_tx = sum(len(block.transactions) for block in self.chain)
        return {
            'blocks': len(self.chain),
            'transactions': total_tx,
            'pending': len(self.pending_transactions),
            'users': len(self.users),
            'valid': self.is_chain_valid()
        }


# Testavimas
if __name__ == "__main__":
    print("="*60)
    print("Pilna v0.1 versija (Centralizuota)")
    print("="*60)
    
    # Sukuriame blockchain
    blockchain = Blockchain(difficulty=2)
    
    # Pridedame vartotojus
    users = [
        User("Alice", "key_alice", 1000.0),
        User("Bob", "key_bob", 500.0),
        User("Charlie", "key_charlie", 750.0),
    ]
    
    for user in users:
        blockchain.add_user(user)
    
    print(f"\nVartotojai: {len(users)}")
    for user in users:
        print(f"  {user}")
    
    # Pridedame transakcijas
    transactions = [
        Transaction("key_alice", "key_bob", 100.0),
        Transaction("key_bob", "key_charlie", 50.0),
        Transaction("key_charlie", "key_alice", 75.0),
        Transaction("key_alice", "key_charlie", 150.0),
        Transaction("key_bob", "key_alice", 25.0),
    ]
    
    for tx in transactions:
        blockchain.add_transaction(tx)
    
    print(f"\nTransakcijos: {len(transactions)}")
    for tx in transactions:
        print(f"  {tx}")
    
    # Kasame bloką
    print("\n" + "="*60)
    print("KASIMO PROCESAS")
    print("="*60)
    
    blockchain.mine_pending_transactions(transactions_per_block=5)
    
    # Rodome rezultatus
    blockchain.print_chain()
    
    # Balansai
    print("\nGALUTINIAI BALANSAI:")
    for user in users:
        print(f"  {user}")
    
    # Statistika
    stats = blockchain.get_statistics()
    print("\nSTATISTIKA:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
