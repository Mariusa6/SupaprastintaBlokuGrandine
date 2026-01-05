import hashlib
import time
import random
from datetime import datetime
from typing import List, Optional, Dict
import json


class User:
    """Vartotojo klasė su vardu, viešuoju raktu ir balansu"""
    
    def __init__(self, name: str, public_key: str, balance: float):
        self.name = name
        self.public_key = public_key
        self.balance = balance
    
    def __repr__(self):
        return f"User(name={self.name}, key={self.public_key[:8]}..., balance={self.balance:.2f})"
    
    def to_dict(self):
        return {
            'name': self.name,
            'public_key': self.public_key,
            'balance': self.balance
        }


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
    
    def is_valid(self, users_dict: Dict[str, User]) -> bool:
        """Patikrina ar transakcija validi"""
        # Tikrina ar siuntėjas egzistuoja
        if self.sender not in users_dict:
            return False
        
        # Tikrina ar gavėjas egzistuoja
        if self.receiver not in users_dict:
            return False
        
        # Tikrina ar suma teigiama
        if self.amount <= 0:
            return False
        
        # Tikrina ar siuntėjas turi pakankamai lėšų
        if users_dict[self.sender].balance < self.amount:
            return False
        
        # Tikrina ar transaction_id teisingas
        expected_hash = hashlib.sha256(
            f"{self.sender}{self.receiver}{self.amount}".encode()
        ).hexdigest()
        
        if self.transaction_id != expected_hash:
            return False
        
        return True
    
    def __repr__(self):
        return f"TX({self.sender[:8]}→{self.receiver[:8]}: {self.amount:.2f})"
    
    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount
        }


class MerkleTree:
    """Merkle Tree implementacija transakcijų hash'ų skaičiavimui"""
    
    def __init__(self, transactions: List[Transaction]):
        self.transactions = transactions
        self.tree = []
        self.root = self._build_tree()
    
    def _build_tree(self) -> str:
        """Sukuria Merkle Tree ir grąžina root hash"""
        if not self.transactions:
            return hashlib.sha256("".encode()).hexdigest()
        
        # Pradinis lygis - transakcijų hash'ai
        current_level = [tx.transaction_id for tx in self.transactions]
        self.tree.append(current_level.copy())
        
        # Kol nelieka vienas hash (root)
        while len(current_level) > 1:
            next_level = []
            
            # Jei nelyginis skaičius, dubliuojame paskutinį
            if len(current_level) % 2 != 0:
                current_level.append(current_level[-1])
            
            # Poruojame ir hash'uojame
            for i in range(0, len(current_level), 2):
                combined = current_level[i] + current_level[i + 1]
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(parent_hash)
            
            self.tree.append(next_level.copy())
            current_level = next_level
        
        return current_level[0]
    
    def get_root(self) -> str:
        """Grąžina Merkle Root hash"""
        return self.root
    
    def __repr__(self):
        return f"MerkleTree(root={self.root[:16]}..., transactions={len(self.transactions)})"


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
    
    def to_dict(self):
        return {
            'prev_block_hash': self.prev_block_hash,
            'timestamp': self.timestamp,
            'version': self.version,
            'merkle_root': self.merkle_root,
            'nonce': self.nonce,
            'difficulty_target': self.difficulty_target
        }


class Block:
    """Bloko klasė su antrašte ir transakcijomis"""
    
    def __init__(self, prev_block_hash: str, transactions: List[Transaction],
                 version: str = "1.0", difficulty_target: int = 3):
        self.version = version
        self.timestamp = time.time()
        self.prev_block_hash = prev_block_hash
        self.transactions = transactions
        self.difficulty_target = difficulty_target
        self.nonce = 0
        
        # Sukuriame Merkle Tree
        self.merkle_tree = MerkleTree(transactions)
        self.merkle_root = self.merkle_tree.get_root()
        
        # Bloko hash bus apskaičiuotas kasimo metu
        self.block_hash = ""
    
    def get_header(self) -> BlockHeader:
        """Grąžina bloko antraštę"""
        return BlockHeader(
            self.prev_block_hash,
            self.timestamp,
            self.version,
            self.merkle_root,
            self.nonce,
            self.difficulty_target
        )
    
    def calculate_hash(self) -> str:
        """Apskaičiuoja bloko hash pagal antraštės duomenis"""
        header_data = (
            f"{self.prev_block_hash}"
            f"{self.timestamp}"
            f"{self.version}"
            f"{self.merkle_root}"
            f"{self.nonce}"
            f"{self.difficulty_target}"
        )
        return hashlib.sha256(header_data.encode()).hexdigest()
    
    def mine_block(self, max_time: float = 5.0, max_attempts: int = None) -> bool:
        """
        Kasa bloką (Proof-of-Work) - ieško nonce, kad hash prasidėtų reikiamu 
        kiekiu nulių
        """
        target = "0" * self.difficulty_target
        attempts = 0
        start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KASIMAS PRADĖTAS")
        print(f"{'='*70}")
        print(f"  Target: hash pradžia '{target}...'")
        print(f"  Max laikas: {max_time}s")
        if max_attempts:
            print(f"  Max bandymų: {max_attempts}")
        print(f"  Transakcijų: {len(self.transactions)}")
        
        while True:
            self.block_hash = self.calculate_hash()
            attempts += 1
            
            # Rodome progresą kas 100000 bandymų
            if attempts % 100000 == 0:
                elapsed = time.time() - start_time
                rate = attempts / elapsed if elapsed > 0 else 0
                print(f"  Bandymas #{attempts:,} | "
                      f"Laikas: {elapsed:.2f}s | "
                      f"Greitis: {rate:,.0f} hash/s | "
                      f"Nonce: {self.nonce}")
            
            # Tikriname ar hash atitinka target
            if self.block_hash.startswith(target):
                elapsed = time.time() - start_time
                rate = attempts / elapsed if elapsed > 0 else 0
                print(f"\nBLOKAS IŠKASTAS!")
                print(f"  Hash: {self.block_hash}")
                print(f"  Nonce: {self.nonce}")
                print(f"  Bandymų: {attempts:,}")
                print(f"  Laikas: {elapsed:.2f}s")
                print(f"  Greitis: {rate:,.0f} hash/s")
                print(f"{'='*70}\n")
                return True
            
            # Tikriname laiko limitą
            if time.time() - start_time > max_time:
                print(f"\nLAIKO LIMITAS PASIEKTAS")
                print(f"  Bandymų: {attempts:,}")
                print(f"  Paskutinis hash: {self.block_hash}")
                print(f"{'='*70}\n")
                return False
            
            # Tikriname bandymų limitą
            if max_attempts and attempts >= max_attempts:
                print(f"\nBANDYMŲ LIMITAS PASIEKTAS")
                print(f"  Bandymų: {attempts:,}")
                print(f"  Paskutinis hash: {self.block_hash}")
                print(f"{'='*70}\n")
                return False
            
            self.nonce += 1
    
    def __repr__(self):
        return (f"Block(hash={self.block_hash[:16]}..., "
                f"prev={self.prev_block_hash[:16]}..., "
                f"txs={len(self.transactions)})")
    
    def to_dict(self):
        return {
            'block_hash': self.block_hash,
            'header': self.get_header().to_dict(),
            'transactions': [tx.to_dict() for tx in self.transactions]
        }


class Blockchain:
    """Blokų grandinės klasė"""
    
    def __init__(self, difficulty: int = 3):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.users: Dict[str, User] = {}
        self.pending_transactions: List[Transaction] = []
        
        # Sukuriame Genesis bloką
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """Sukuria pirminį (Genesis) bloką"""
        print("\n" + "="*70)
        print("KURIAMAS GENESIS BLOKAS")
        print("="*70)
        
        genesis_block = Block(
            prev_block_hash="0" * 64,
            transactions=[],
            version="1.0",
            difficulty_target=self.difficulty
        )
        
        # Genesis blokas nekasamas, tiesiog priskiriamas hash
        genesis_block.block_hash = genesis_block.calculate_hash()
        
        self.chain.append(genesis_block)
        
        print(f"Genesis blokas sukurtas!")
        print(f"  Hash: {genesis_block.block_hash}")
        print(f"  Timestamp: {datetime.fromtimestamp(genesis_block.timestamp)}")
        print("="*70 + "\n")
    
    def get_last_block(self) -> Block:
        """Grąžina paskutinį bloką grandinėje"""
        return self.chain[-1]
    
    def add_user(self, user: User):
        """Prideda vartotoją į sistemą"""
        self.users[user.public_key] = user
    
    def add_transaction(self, transaction: Transaction):
        """Prideda transakciją į laukiančių sąrašą"""
        self.pending_transactions.append(transaction)
    
    def create_candidate_blocks(self, num_candidates: int = 5,
                                transactions_per_block: int = 100) -> List[Block]:
        """Sukuria kelis kandidatinius blokus kasimui"""
        candidates = []
        
        print(f"\nKuriami {num_candidates} kandidatiniai blokai...")
        print(f"  Transakcijų laukia: {len(self.pending_transactions)}")
        print(f"  Transakcijų bloke: {transactions_per_block}")
        
        for i in range(num_candidates):
            if len(self.pending_transactions) < transactions_per_block:
                break
            
            # Atsitiktinai pasirenkame transakcijas
            selected_txs = random.sample(
                self.pending_transactions,
                min(transactions_per_block, len(self.pending_transactions))
            )
            
            # Filtruojame tik valid transakcijas
            valid_txs = [tx for tx in selected_txs if tx.is_valid(self.users)]
            
            if not valid_txs:
                continue
            
            block = Block(
                prev_block_hash=self.get_last_block().block_hash,
                transactions=valid_txs,
                difficulty_target=self.difficulty
            )
            
            candidates.append(block)
            print(f"  ✓ Kandidatas #{i+1}: {len(valid_txs)} validžių transakcijų")
        
        return candidates
    
    def mine_and_add_block(self, max_time: float = 5.0, max_attempts: int = None) -> bool:
        """
        Sukuria kelis kandidatinius blokus, bando juos iškasti ir prideda 
        pirmą sėkmingai iškastą
        """
        candidates = self.create_candidate_blocks()
        
        if not candidates:
            print("Nepavyko sukurti kandidatinių blokų")
            return False
        
        # Bandome kasti kiekvieną kandidatą
        for i, block in enumerate(candidates):
            print(f"\nBandomas kandidatas #{i+1}/{len(candidates)}")
            
            if block.mine_block(max_time=max_time, max_attempts=max_attempts):
                # Blokas iškastas! Pridedame jį
                self._add_mined_block(block)
                return True
        
        # Jei nė vienas blokas neiškastas, pabandome dar kartą su didesniu laiku
        print(f"\nNė vienas blokas neiškastas per {max_time}s")
        print(f"Bandoma dar kartą su dvigubai didesniu laiku...")
        
        for i, block in enumerate(candidates):
            if block.mine_block(max_time=max_time * 2, max_attempts=max_attempts):
                self._add_mined_block(block)
                return True
        
        return False
    
    def _add_mined_block(self, block: Block):
        """Prideda iškastą bloką į grandinę ir atnaujina balansus"""
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
        print(f"  Hash: {block.block_hash}")
        print(f"  Prev hash: {block.prev_block_hash[:32]}...")
        print(f"  Transakcijų: {len(block.transactions)}")
        print(f"  Merkle root: {block.merkle_root[:32]}...")
        print(f"  Nonce: {block.nonce}")
        print(f"  Liko transakcijų: {len(self.pending_transactions)}")
        print(f"{'='*70}\n")
    
    def is_chain_valid(self) -> bool:
        """Patikrina ar visa grandinė validi"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Tikriname ar hash teisingas
            if current_block.block_hash != current_block.calculate_hash():
                return False
            
            # Tikriname ar prev_hash sutampa
            if current_block.prev_block_hash != previous_block.block_hash:
                return False
            
            # Tikriname ar hash atitinka difficulty
            target = "0" * current_block.difficulty_target
            if not current_block.block_hash.startswith(target):
                return False
        
        return True
    
    def print_chain(self):
        """Išspausdina visą grandinę gražiai"""
        print("\n" + "="*70)
        print("BLOKŲ GRANDINĖ")
        print("="*70)
        
        for i, block in enumerate(self.chain):
            print(f"\n{'─'*70}")
            print(f"Blokas #{i}")
            print(f"{'─'*70}")
            print(f"Hash:         {block.block_hash}")
            print(f"Prev Hash:    {block.prev_block_hash}")
            print(f"Timestamp:    {datetime.fromtimestamp(block.timestamp)}")
            print(f"Merkle Root:  {block.merkle_root}")
            print(f"Nonce:        {block.nonce}")
            print(f"Difficulty:   {block.difficulty_target}")
            print(f"Transakcijų:  {len(block.transactions)}")
            
            if block.transactions and i > 0:  # Nerodome Genesis bloko transakcijų
                print(f"\nPirmos 5 transakcijos:")
                for j, tx in enumerate(block.transactions[:5]):
                    sender_name = self.users[tx.sender].name if tx.sender in self.users else "Unknown"
                    receiver_name = self.users[tx.receiver].name if tx.receiver in self.users else "Unknown"
                    print(f"  {j+1}. {sender_name} → {receiver_name}: {tx.amount:.2f}")
                
                if len(block.transactions) > 5:
                    print(f"  ... ir dar {len(block.transactions) - 5} transakcijų")
        
        print(f"\n{'='*70}")
        print(f"Iš viso blokų: {len(self.chain)}")
        print(f"Grandinė valid: {'Taip' if self.is_chain_valid() else 'Ne'}")
        print(f"{'='*70}\n")
    
    def get_statistics(self):
        """Grąžina statistiką apie grandinę"""
        total_transactions = sum(len(block.transactions) for block in self.chain)
        
        stats = {
            'total_blocks': len(self.chain),
            'total_transactions': total_transactions,
            'total_users': len(self.users),
            'pending_transactions': len(self.pending_transactions),
            'chain_valid': self.is_chain_valid()
        }
        
        return stats
