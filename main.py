import hashlib
import time
import random
from typing import List, Dict, Optional


class User:
    """Vartotojo klasė"""
    
    def __init__(self, name: str, public_key: str, balance: float):
        self.name = name
        self.public_key = public_key
        self.balance = balance


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
    """Bloko klasė su laiko limitais"""
    
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
                print(f"  Iškasta! Nonce: {self.nonce}, "
                      f"Bandymų: {attempts:,}, Laikas: {elapsed:.2f}s")
                return True
            
            if time.time() - start_time > max_time:
                return False
            
            if max_attempts and attempts >= max_attempts:
                return False
            
            self.nonce += 1


class Blockchain:
    """
    Blockchain klasė - dabar su kandidatiniais blokais!
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
        """
        Kuria kandidatinius blokus
        
        Kiekvienas kandidatas turi skirtingas atsitiktines transakcijas.
        Tai imituoja decentralizuotą kasimą - kiekvienas kasėjas turi savo bloką.
        
        Args:
            num_candidates: Kiek kandidatų sukurti
            transactions_per_block: Transakcijų skaičius bloke
        
        Returns:
            List[Block]: Kandidatinių blokų sąrašas
        """
        candidates = []
        
        print(f"\nKuriami {num_candidates} kandidatiniai blokai...")
        print(f"  Transakcijų laukia: {len(self.pending_transactions)}")
        print(f"  Transakcijų bloke: {transactions_per_block}")
        
        if len(self.pending_transactions) < transactions_per_block:
            print(f"  Per mažai transakcijų!")
            return []
        
        for i in range(num_candidates):
            # Atsitiktinai pasirenkame transakcijas
            # Kiekvienas kandidatas gali turėti skirtingas TX
            selected_txs = random.sample(
                self.pending_transactions,
                min(transactions_per_block, len(self.pending_transactions))
            )
            
            # Filtruojame tik valid transakcijas
            valid_txs = [tx for tx in selected_txs if tx.is_valid(self.users)]
            
            if not valid_txs:
                print(f"  Kandidatas #{i+1}: nėra valid transakcijų")
                continue
            
            # Sukuriame kandidatinį bloką
            candidate = Block(
                prev_block_hash=self.get_last_block().block_hash,
                transactions=valid_txs,
                difficulty_target=self.difficulty
            )
            
            candidates.append(candidate)
            print(f"  ✓ Kandidatas #{i+1}: {len(valid_txs)} valid transakcijų, "
                  f"merkle: {candidate.merkle_root[:16]}...")
        
        print(f"\n  Sukurta kandidatų: {len(candidates)}")
        return candidates


# Testavimas
if __name__ == "__main__":
    print("="*70)
    print("Kandidatiniai blokai")
    print("="*70)
    
    # Sukuriame blockchain
    blockchain = Blockchain(difficulty=2)
    
    # Pridedame vartotojus
    users_list = [
        User("Alice", "key_alice", 1000.0),
        User("Bob", "key_bob", 800.0),
        User("Charlie", "key_charlie", 600.0),
        User("Diana", "key_diana", 400.0),
    ]
    
    for user in users_list:
        blockchain.add_user(user)
    
    print(f"\nPridėta {len(users_list)} vartotojų")
    
    # Sukuriame daug transakcijų
    print(f"\nGeneruojamos transakcijos...")
    for i in range(50):
        sender = random.choice(users_list)
        receiver = random.choice(users_list)
        while sender.public_key == receiver.public_key:
            receiver = random.choice(users_list)
        
        amount = random.uniform(10, 100)
        tx = Transaction(sender.public_key, receiver.public_key, amount)
        blockchain.add_transaction(tx)
    
    print(f"  Sukurta {len(blockchain.pending_transactions)} transakcijų")
    
    # Test 1: Sukuriame 3 kandidatus
    print("\n" + "="*70)
    print("TEST 1: Sukuriame 3 kandidatinius blokus po 10 TX")
    print("="*70)
    
    candidates = blockchain.create_candidate_blocks(
        num_candidates=3,
        transactions_per_block=10
    )
    
    print(f"\nKandidatų palyginimas:")
    for i, candidate in enumerate(candidates):
        print(f"\n  Kandidatas #{i+1}:")
        print(f"    TX: {len(candidate.transactions)}")
        print(f"    Merkle: {candidate.merkle_root[:32]}...")
        print(f"    Pirma TX: {candidate.transactions[0] if candidate.transactions else 'N/A'}")
    
    # Test 2: Bandomekasti pirmus 2 kandidatus
    print("\n" + "="*70)
    print("TEST 2: Bandome kasti pirmus 2 kandidatus")
    print("="*70)
    
    for i in range(min(2, len(candidates))):
        print(f"\nKasimas kandidatas #{i+1}:")
        success = candidates[i].mine_block(max_time=5.0)
        
        if success:
            print(f"  Kandidatas #{i+1} LAIMĖJO!")
            print(f"  Hash: {candidates[i].block_hash[:32]}...")
            break
        else:
            print(f"  Kandidatas #{i+1} timeout")