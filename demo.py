#!/usr/bin/env python3
"""
Blockchain Demo - Mažesnė versija vizualizacijai
Sukuria tik kelis vartotojus ir kelias transakcijas aiškumui
"""

import time
from blockchain import User, Transaction, Blockchain


def print_separator(char="=", width=70):
    """Spausdina skyriklį"""
    print("\n" + char * width)


def demo_small_blockchain():
    """Demonstracija su mažu duomenų kiekiu"""
    print_separator()
    print("BLOCKCHAIN MINI DEMO")
    print_separator()
    
    # Sukuriame blockchain
    blockchain = Blockchain(difficulty=5)
    
    # Sukuriame 5 vartotojus
    print("\nKuriami vartotojai:")
    users = [
        User("Alice", "key_alice", 1000.0),
        User("Bob", "key_bob", 500.0),
        User("Charlie", "key_charlie", 750.0),
        User("Diana", "key_diana", 1200.0),
        User("Eve", "key_eve", 300.0)
    ]
    
    for user in users:
        blockchain.add_user(user)
        print(f"  ✓ {user.name}: {user.balance:.2f}")
    
    # Sukuriame 20 transakcijų
    print("\nKuriamos transakcijos:")
    transactions = [
        # Round 1
        Transaction("key_alice", "key_bob", 100.0),
        Transaction("key_bob", "key_charlie", 50.0),
        Transaction("key_charlie", "key_diana", 75.0),
        Transaction("key_diana", "key_eve", 200.0),
        Transaction("key_eve", "key_alice", 50.0),
        # Round 2
        Transaction("key_alice", "key_charlie", 150.0),
        Transaction("key_bob", "key_diana", 100.0),
        Transaction("key_charlie", "key_eve", 25.0),
        Transaction("key_diana", "key_alice", 300.0),
        Transaction("key_eve", "key_bob", 75.0),
        # Round 3
        Transaction("key_alice", "key_eve", 200.0),
        Transaction("key_bob", "key_alice", 50.0),
        Transaction("key_charlie", "key_bob", 100.0),
        Transaction("key_diana", "key_charlie", 150.0),
        Transaction("key_eve", "key_diana", 25.0),
        # Round 4
        Transaction("key_alice", "key_diana", 100.0),
        Transaction("key_bob", "key_charlie", 75.0),
        Transaction("key_charlie", "key_alice", 50.0),
        Transaction("key_diana", "key_bob", 100.0),
        Transaction("key_eve", "key_charlie", 50.0),
    ]
    
    for i, tx in enumerate(transactions):
        blockchain.add_transaction(tx)
        sender_name = blockchain.users[tx.sender].name
        receiver_name = blockchain.users[tx.receiver].name
        print(f"  {i+1}. {sender_name} → {receiver_name}: {tx.amount:.2f}")
    
    # Kasame 2 blokus
    print_separator()
    print("BLOCKCHAIN KASIMAS")
    print_separator()
    
    for block_num in range(1, 3):
        print(f"\n{'#'*70}")
        print(f"# BLOKAS #{block_num}")
        print(f"{'#'*70}")
        
        # Override kandidatinių blokų kūrimą su mažesniu transakcijų skaičiumi
        candidates = blockchain.create_candidate_blocks(
            num_candidates=3,
            transactions_per_block=10
        )
        
        if not candidates:
            print(f"Nepavyko sukurti kandidatinių blokų #{block_num}")
            break
        
        # Bandome kasti pirmą kandidatą
        success = False
        for candidate in candidates:
            if candidate.mine_block(max_time=5.0):
                blockchain._add_mined_block(candidate)
                success = True
                break
        
        if not success:
            print(f"Nepavyko iškasti bloko #{block_num}")
            break
        
        time.sleep(0.5)  # Trumpa pauzė vizualumui
    
    # Rodome galutinę grandinę
    blockchain.print_chain()
    
    # Rodome galutinius balansus
    print_separator()
    print("GALUTINIAI BALANSAI")
    print_separator()
    
    for user in users:
        balance_change = user.balance - {
            "key_alice": 1000.0,
            "key_bob": 500.0,
            "key_charlie": 750.0,
            "key_diana": 1200.0,
            "key_eve": 300.0
        }[user.public_key]
        
        change_symbol = "+" if balance_change > 0 else ""
        print(f"  {user.name:10} | {user.balance:8.2f} | "
              f"{change_symbol}{balance_change:.2f}")
    
    print_separator()
    
    # Validuojame grandinę
    print("\nGRANDINĖS VALIDACIJA:")
    is_valid = blockchain.is_chain_valid()
    print(f"  Grandinė valid: {'TAIP' if is_valid else 'NE'}")
    
    # Statistika
    stats = blockchain.get_statistics()
    print(f"  Blokų: {stats['total_blocks']}")
    print(f"  Transakcijų: {stats['total_transactions']}")
    print(f"  Liko transakcijų: {stats['pending_transactions']}")
    
    print_separator()


def demo_merkle_tree_visualization():
    """Demonstracija Merkle Tree vizualizacijai"""
    from blockchain import MerkleTree
    
    print_separator()
    print("🌲 MERKLE TREE VIZUALIZACIJA")
    print_separator()
    
    # Sukuriame 4 transakcijas
    transactions = [
        Transaction("sender1", "receiver1", 10.0),
        Transaction("sender2", "receiver2", 20.0),
        Transaction("sender3", "receiver3", 30.0),
        Transaction("sender4", "receiver4", 40.0),
    ]
    
    print("\nTransakcijos:")
    for i, tx in enumerate(transactions):
        print(f"  TX{i+1}: {tx.transaction_id[:16]}...")
    
    # Sukuriame Merkle Tree
    merkle = MerkleTree(transactions)
    
    print("\nMerkle Tree struktūra:")
    print("  (Kiekvienas lygis yra hash'ų sąrašas)")
    print()
    
    for level, hashes in enumerate(merkle.tree):
        print(f"  Level {level}: {len(hashes)} hash(es)")
        for i, h in enumerate(hashes):
            print(f"    [{i}] {h[:32]}...")
        print()
    
    print(f"Merkle Root: {merkle.root}")
    print(f"   (Viršutinis hash, atstovaujantis visas transakcijas)")
    
    print_separator()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("BLOCKCHAIN DEMONSTRACIJA PRASIDEDA")
    print("="*70)
    print("Ši demo versija naudoja mažesnį duomenų kiekį")
    print("kad būtų aiškesnis blockchain veikimo principas.")
    print("="*70)
    
    # Paleisti mini blockchain
    demo_small_blockchain()
    
    # Merkle Tree vizualizacija
    demo_merkle_tree_visualization()
    
    print("\n" + "="*70)
    print("DEMONSTRACIJA BAIGTA")
    print("="*70)
