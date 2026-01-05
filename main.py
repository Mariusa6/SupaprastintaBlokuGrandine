import hashlib
import time
import random
from datetime import datetime
from typing import List, Dict, Optional


class User:
    """Vartotojo klasė"""
    
    def __init__(self, name: str, public_key: str, balance: float):
        self.name = name
        self.public_key = public_key
        self.balance = balance
    
    def __repr__(self):
        return f"User({self.name}, {self.balance:.2f})"


class Transaction:
    """Transakcijos klasė su validacija"""
    
    def __init__(self, sender: str, receiver: str, amount: float):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.transaction_id = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        data = f"{self.sender}{self.receiver}{self.amount}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def is_valid(self, users_dict: Dict[str, User]) -> bool:
        if self.sender not in users_dict or self.receiver not in users_dict:
            return False
        if self.amount <= 0:
            return False
        if users_dict[self.sender].balance < self.amount:
            return False
        expected_hash = hashlib.sha256(
            f"{self.sender}{self.receiver}{self.amount}".encode()
        ).hexdigest()
        return self.transaction_id == expected_hash
    
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
    
    def mine_block(self, max_time: float = 5.0, max_attempts: Optional[int] = None) -> bool:
        target = "0" * self.difficulty_target
        attempts = 0
        start_time = time.time()
        
        while True:
            self.block_hash = self.calculate_hash()
            attempts += 1
            
            if self.block_hash.startswith(target):
                elapsed = time.time() - start_time
                rate = attempts / elapsed if elapsed > 0 else 0
                print(f"    Iškasta! Nonce: {self.nonce}, "
                      f"Bandymų: {attempts:,}, Laikas: {elapsed:.2f}s, "
                      f"Greitis: {rate:,.0f} hash/s")
                return True
            
            if time.time() - start_time > max_time:
                return False
            if max_attempts and attempts >= max_attempts:
                return False
            
            self.nonce += 1
    
    def __repr__(self):
        return f"Block(hash={self.block_hash[:16]}..., tx={len(self.transactions)})"


class Blockchain:
    """
    Pilna decentralizuota blockchain
    """
    
    def __init__(self, difficulty: int = 3):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.users: Dict[str, User] = {}
        self.pending_transactions: List[Transaction] = []
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        genesis = Block("0"*64, [], difficulty_target=self.difficulty)
        genesis.block_hash = genesis.calculate_hash()
        self.chain.append(genesis)
        print("Genesis blokas sukurtas")
    
    def get_last_block(self) -> Block:
        return self.chain[-1]
    
    def add_user(self, user: User):
        self.users[user.public_key] = user
    
    def add_transaction(self, transaction: Transaction):
        self.pending_transactions.append(transaction)
    
    def create_candidate_blocks(self, num_candidates: int = 5,
                               transactions_per_block: int = 100) -> List[Block]:
        """Kuria kandidatinius blokus"""
        candidates = []
        
        if len(self.pending_transactions) < transactions_per_block:
            return []
        
        for i in range(num_candidates):
            selected_txs = random.sample(
                self.pending_transactions,
                min(transactions_per_block, len(self.pending_transactions))
            )
            valid_txs = [tx for tx in selected_txs if tx.is_valid(self.users)]
            
            if not valid_txs:
                continue
            
            candidate = Block(
                prev_block_hash=self.get_last_block().block_hash,
                transactions=valid_txs,
                difficulty_target=self.difficulty
            )
            candidates.append(candidate)
        
        return candidates
    
    def mine_and_add_block(self, max_time: float = 5.0, max_attempts: Optional[int] = None) -> bool:
        """
        Decentralizuotas kasimas
        
        Kuria kelis kandidatinius blokus ir bando kasti kiekvieną.
        Pirmas iškastas blokas pridedamas į grandinę.
        Jei nė vienas neiškastas - padidina laiką ir bando dar kartą.
        
        Tai imituoja decentralizuotą tinklą, kur keli kasėjai konkuruoja.
        """
        # 1. Sukuriame kandidatinius blokus
        candidates = self.create_candidate_blocks(num_candidates=5, transactions_per_block=100)
        
        if not candidates:
            print("Nepavyko sukurti kandidatinių blokų")
            return False
        
        print(f"\nSukurta {len(candidates)} kandidatinių blokų")
        
        # 2. Bandome kasti kiekvieną kandidatą
        print(f"\nKASIMAS (max {max_time}s per kandidatą):")
        
        for i, block in enumerate(candidates):
            print(f"\n  Kandidatas #{i+1}/{len(candidates)}:")
            
            if block.mine_block(max_time=max_time, max_attempts=max_attempts):
                # Blokas iškastas! Pridedame jį
                self._add_mined_block(block)
                return True
        
        # 3. Jei nė vienas neiškastas - pabandome su didesniu laiku
        print(f"\nNė vienas kandidatas neiškastas per {max_time}s")
        print(f"Bandoma dar kartą su {max_time*2}s...")
        
        for i, block in enumerate(candidates):
            print(f"\n  Kandidatas #{i+1}/{len(candidates)} (2nd attempt):")
            
            if block.mine_block(max_time=max_time * 2, max_attempts=max_attempts):
                self._add_mined_block(block)
                return True
        
        print(f"\nNepavyko iškasti bloko net su {max_time*2}s")
        return False
    
    def _add_mined_block(self, block: Block):
        """
        Prideda iškastą bloką ir atnaujina balansus
        """
        # Pašaliname transakcijas iš pending
        for tx in block.transactions:
            if tx in self.pending_transactions:
                self.pending_transactions.remove(tx)
            
            # Atnaujiname balansus
            if tx.sender in self.users and tx.receiver in self.users:
                self.users[tx.sender].balance -= tx.amount
                self.users[tx.receiver].balance += tx.amount
        
        # Pridedame bloką į grandinę
        self.chain.append(block)
        
        print(f"\n{'='*70}")
        print(f"BLOKAS PRIDĖTAS Į GRANDINĘ")
        print(f"{'='*70}")
        print(f"  Bloko numeris: {len(self.chain) - 1}")
        print(f"  Hash: {block.block_hash[:32]}...")
        print(f"  Transakcijų: {len(block.transactions)}")
        print(f"  Merkle root: {block.merkle_root[:32]}...")
        print(f"  Nonce: {block.nonce}")
        print(f"  Liko TX: {len(self.pending_transactions)}")
        print(f"{'='*70}")
    
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
    
    def print_statistics(self):
        """Statistika"""
        total_tx = sum(len(block.transactions) for block in self.chain)
        print(f"\nSTATISTIKA:")
        print(f"  Blokų: {len(self.chain)}")
        print(f"  Transakcijų: {total_tx}")
        print(f"  Liko TX: {len(self.pending_transactions)}")
        print(f"  Vartotojų: {len(self.users)}")
        print(f"  Grandinė valid: {'yes' if self.is_chain_valid() else 'no'}")


# Testavimas
if __name__ == "__main__":
    print("="*70)
    print("Pilna decentralizuota blockchain (RELEASE)")
    print("="*70)
    
    # Sukuriame blockchain
    blockchain = Blockchain(difficulty=2)
    
    # Pridedame vartotojus
    users = [
        User("Alice", "alice", 5000.0),
        User("Bob", "bob", 4000.0),
        User("Charlie", "charlie", 3000.0),
        User("Diana", "diana", 2000.0),
    ]
    
    for user in users:
        blockchain.add_user(user)
    
    print(f"\nVartotojai: {len(users)}")
    
    # Generuojame transakcijas
    print(f"\nGeneruojamos transakcijos...")
    for i in range(150):
        sender = random.choice(users)
        receiver = random.choice(users)
        while sender.public_key == receiver.public_key:
            receiver = random.choice(users)
        amount = random.uniform(10, 100)
        tx = Transaction(sender.public_key, receiver.public_key, amount)
        blockchain.add_transaction(tx)
    
    print(f"  Sukurta {len(blockchain.pending_transactions)} transakcijų")
    
    # Kasame blokus (v0.2 decentralizuota versija)
    print("\n" + "="*70)
    print("DECENTRALIZUOTAS KASIMAS")
    print("="*70)
    
    for round in range(1, 3):
        print(f"\n{'#'*70}")
        print(f"# RAUNDAS #{round}")
        print(f"{'#'*70}")
        
        success = blockchain.mine_and_add_block(max_time=3.0)
        
        if not success:
            print(f"Raundas #{round} nepavyko")
            break
    
    # Rezultatai
    blockchain.print_statistics()
    
    # Balansai
    print(f"\nGALUTINIAI BALANSAI:")
    for user in users:
        print(f"  {user}")
