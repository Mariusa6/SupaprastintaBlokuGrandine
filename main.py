import hashlib
import time
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
        """Validuoja transakciją"""
        if self.sender not in users_dict or self.receiver not in users_dict:
            return False
        if self.amount <= 0:
            return False
        if users_dict[self.sender].balance < self.amount:
            return False
        expected_hash = hashlib.sha256(
            f"{self.sender}{self.receiver}{self.amount}".encode()
        ).hexdigest()
        if self.transaction_id != expected_hash:
            return False
        return True


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
    """Bloko klasė - dabar su laiko limitais!"""
    
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
        """
        Kasimas su laiko ir bandymų limitais
        
        Args:
            max_time: Maksimalus kasimo laikas sekundėmis
            max_attempts: Maksimalus bandymų skaičius (None = neribotas)
        
        Returns:
            True jei iškasta, False jei timeout
        """
        target = "0" * self.difficulty_target
        attempts = 0
        start_time = time.time()
        
        print(f"\nKASIMAS PRADĖTAS")
        print(f"  Target: {target}...")
        print(f"  Max laikas: {max_time}s")
        if max_attempts:
            print(f"  Max bandymų: {max_attempts:,}")
        
        while True:
            self.block_hash = self.calculate_hash()
            attempts += 1
            
            # Rodome progresą kas 50000 bandymų
            if attempts % 50000 == 0:
                elapsed = time.time() - start_time
                rate = attempts / elapsed if elapsed > 0 else 0
                print(f"  Bandymas #{attempts:,} | "
                      f"Laikas: {elapsed:.2f}s | "
                      f"Greitis: {rate:,.0f} hash/s")
            
            # Tikriname ar hash atitinka target
            if self.block_hash.startswith(target):
                elapsed = time.time() - start_time
                rate = attempts / elapsed if elapsed > 0 else 0
                print(f"\n  BLOKAS IŠKASTAS!")
                print(f"  Hash: {self.block_hash[:32]}...")
                print(f"  Nonce: {self.nonce}")
                print(f"  Bandymų: {attempts:,}")
                print(f"  Laikas: {elapsed:.2f}s")
                print(f"  Greitis: {rate:,.0f} hash/s")
                return True
            
            # Tikriname laiko limitą
            if time.time() - start_time > max_time:
                elapsed = time.time() - start_time
                print(f"\n  LAIKO LIMITAS PASIEKTAS ({elapsed:.2f}s)")
                print(f"  Bandymų: {attempts:,}")
                print(f"  Paskutinis hash: {self.block_hash[:32]}...")
                return False
            
            # Tikriname bandymų limitą
            if max_attempts and attempts >= max_attempts:
                elapsed = time.time() - start_time
                print(f"\n  BANDYMŲ LIMITAS PASIEKTAS ({attempts:,})")
                print(f"  Laikas: {elapsed:.2f}s")
                print(f"  Paskutinis hash: {self.block_hash[:32]}...")
                return False
            
            self.nonce += 1


# Testavimas
if __name__ == "__main__":
    
    # Sukuriame test transakcijas
    users = {
        "alice": User("Alice", "alice", 1000.0),
        "bob": User("Bob", "bob", 500.0),
    }
    
    txs = [
        Transaction("alice", "bob", 100.0),
        Transaction("bob", "alice", 50.0),
    ]
    
    # Test 1: Lengvas difficulty - turėtų greitai iškasti
    print("\n" + "="*70)
    print("TEST 1: Lengvas difficulty (2) - turėtų suspėti")
    print("="*70)
    
    block1 = Block("0"*64, txs, difficulty_target=2)
    success = block1.mine_block(max_time=5.0)
    print(f"\n  Rezultatas: {'Iškasta' if success else 'Timeout'}")
    
    # Test 2: Sunkus difficulty - greičiausiai timeout
    print("\n" + "="*70)
    print("TEST 2: Sunkus difficulty (5) - greičiausiai timeout")
    print("="*70)
    
    block2 = Block("0"*64, txs, difficulty_target=5)
    success = block2.mine_block(max_time=3.0)
    print(f"\n  Rezultatas: {'Iškasta' if success else 'Timeout'}")
    
    # Test 3: Su bandymų limitu
    print("\n" + "="*70)
    print("TEST 3: Difficulty 3 su 1000 bandymų limitu")
    print("="*70)
    
    block3 = Block("0"*64, txs, difficulty_target=3)
    success = block3.mine_block(max_time=10.0, max_attempts=1000)
    print(f"\n  Rezultatas: {'Iškasta' if success else 'Limitas'}")
    
    # Test 4: Normalus kasimas
    print("\n" + "="*70)
    print("TEST 4: Normalus kasimas (difficulty 3, 10s)")
    print("="*70)
    
    block4 = Block("0"*64, txs, difficulty_target=3)
    success = block4.mine_block(max_time=10.0)
    print(f"\n  Rezultatas: {'Iškasta' if success else 'Timeout'}")

