#!/usr/bin/env python3
"""
Supaprastinta Blockchain implementacija
Versija: v0.2
Autorius: [Jūsų vardas]
Data: 2025-01-05
"""

import random
import string
import time
from blockchain import User, Transaction, Blockchain


def generate_random_key(length: int = 64) -> str:
    """Sugeneruoja atsitiktinį viešąjį raktą (hex formatu)"""
    return ''.join(random.choices(string.hexdigits.lower(), k=length))


def generate_users(num_users: int = 1000) -> list:
    """Sugeneruoja vartotojus su atsitiktiniais balansais"""
    print("\n" + "="*70)
    print(f"👥 GENERUOJAMI VARTOTOJAI")
    print("="*70)
    
    names = [
        "Jonas", "Petras", "Marija", "Ona", "Antanas", "Kazys", "Jūratė",
        "Rūta", "Darius", "Vytautas", "Gintarė", "Laima", "Mindaugas",
        "Algirdas", "Birutė", "Daiva", "Saulius", "Rasa", "Tomas", "Eglė"
    ]
    
    users = []
    start_time = time.time()
    
    for i in range(num_users):
        name = f"{random.choice(names)}_{i}"
        public_key = generate_random_key()
        balance = random.uniform(100, 1000000)
        
        user = User(name, public_key, balance)
        users.append(user)
        
        # Rodome progresą
        if (i + 1) % 200 == 0 or i == num_users - 1:
            progress = (i + 1) / num_users * 100
            print(f"  Progresas: {progress:.1f}% ({i+1}/{num_users})")
    
    elapsed = time.time() - start_time
    print(f"\nSugeneruota {num_users} vartotojų per {elapsed:.2f}s")
    print(f"  Vidutinis balansas: {sum(u.balance for u in users)/len(users):.2f}")
    print(f"  Min balansas: {min(u.balance for u in users):.2f}")
    print(f"  Max balansas: {max(u.balance for u in users):.2f}")
    print("="*70 + "\n")
    
    return users


def generate_transactions(users: list, num_transactions: int = 10000) -> list:
    """Sugeneruoja transakcijas tarp vartotojų"""
    print("\n" + "="*70)
    print(f"GENERUOJAMOS TRANSAKCIJOS")
    print("="*70)
    
    transactions = []
    start_time = time.time()
    
    for i in range(num_transactions):
        # Pasirenkame atsitiktinius siuntėją ir gavėją
        sender = random.choice(users)
        receiver = random.choice(users)
        
        # Užtikriname, kad siuntėjas ir gavėjas nesutampa
        while sender.public_key == receiver.public_key:
            receiver = random.choice(users)
        
        # Suma - iki 30% siuntėjo balanso
        max_amount = sender.balance * 0.3
        amount = random.uniform(1, max_amount) if max_amount > 1 else random.uniform(0.1, 1)
        
        tx = Transaction(sender.public_key, receiver.public_key, amount)
        transactions.append(tx)
        
        # Rodome progresą
        if (i + 1) % 2000 == 0 or i == num_transactions - 1:
            progress = (i + 1) / num_transactions * 100
            print(f"  Progresas: {progress:.1f}% ({i+1}/{num_transactions})")
    
    elapsed = time.time() - start_time
    print(f"\nSugeneruota {num_transactions} transakcijų per {elapsed:.2f}s")
    print(f"  Vidutinė suma: {sum(tx.amount for tx in transactions)/len(transactions):.2f}")
    print("="*70 + "\n")
    
    return transactions


def print_sample_data(users: list, transactions: list):
    """Išspausdina pavyzdžius vartotojų ir transakcijų"""
    print("\n" + "="*70)
    print("DUOMENŲ PAVYZDŽIAI")
    print("="*70)
    
    print("\n🔹 Pirmi 5 vartotojai:")
    for i, user in enumerate(users[:5]):
        print(f"  {i+1}. {user.name}")
        print(f"     Key: {user.public_key[:32]}...")
        print(f"     Balansas: {user.balance:.2f}")
    
    print("\n🔹 Pirmos 5 transakcijos:")
    for i, tx in enumerate(transactions[:5]):
        print(f"  {i+1}. TX ID: {tx.transaction_id[:32]}...")
        print(f"     Siuntėjas: {tx.sender[:16]}...")
        print(f"     Gavėjas: {tx.receiver[:16]}...")
        print(f"     Suma: {tx.amount:.2f}")
    
    print("="*70 + "\n")


def main():
    """Pagrindinė programa"""
    print("\n" + "="*70)
    print("BLOCKCHAIN SIMULIACIJA PRASIDEDA")
    print("="*70)
    print("Versija: v0.2")
    print("Data:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)
    
    # 1. Generuojame vartotojus
    users = generate_users(num_users=1000)
    
    # 2. Generuojame transakcijas
    transactions = generate_transactions(users, num_transactions=10000)
    
    # 3. Rodom pavyzdžius
    print_sample_data(users, transactions)
    
    # 4. Sukuriame blockchain
    print("\n" + "="*70)
    print("BLOCKCHAIN INICIALIZATION")
    print("="*70)
    
    blockchain = Blockchain(difficulty=5)
    
    # Pridedame vartotojus į blockchain
    for user in users:
        blockchain.add_user(user)
    
    print(f"Pridėta {len(users)} vartotojų į blockchain")
    
    # Pridedame transakcijas į pending
    for tx in transactions:
        blockchain.add_transaction(tx)
    
    print(f"Pridėta {len(transactions)} transakcijų į pending sąrašą")
    print("="*70)
    
    # 5. Kasame blokus kol nebeliko transakcijų
    block_count = 0
    max_blocks = 100  # Saugiklis, kad nesukurtume per daug blokų
    
    print("\n" + "="*70)
    print("PRADEDAMAS KASIMO PROCESAS")
    print("="*70)
    print(f"Pending transakcijų: {len(blockchain.pending_transactions)}")
    print(f"Difficulty: {blockchain.difficulty}")
    print("="*70)
    
    while blockchain.pending_transactions and block_count < max_blocks:
        block_count += 1
        
        print(f"\n{'#'*70}")
        print(f"# BLOKAS #{block_count}")
        print(f"{'#'*70}")
        
        success = blockchain.mine_and_add_block(max_time=5.0)
        
        if not success:
            print(f"\nNepavyko iškasti bloko #{block_count}")
            print(f"  Galite:")
            print(f"   - Sumažinti difficulty")
            print(f"   - Padidinti max_time")
            print(f"   - Pagerinti hash funkciją")
            break
        
        # Kas 5 blokus rodome statistiką
        if block_count % 5 == 0:
            stats = blockchain.get_statistics()
            print(f"\nTARPINĖ STATISTIKA:")
            print(f"  Blokų grandinėje: {stats['total_blocks']}")
            print(f"  Apdorotų transakcijų: {stats['total_transactions']}")
            print(f"  Liko transakcijų: {stats['pending_transactions']}")
    
    # 6. Finalinė statistika ir grandinės išvedimas
    print("\n" + "="*70)
    print("FINALINĖ STATISTIKA")
    print("="*70)
    
    stats = blockchain.get_statistics()
    print(f"  Iš viso blokų: {stats['total_blocks']}")
    print(f"  Iš viso transakcijų: {stats['total_transactions']}")
    print(f"  Iš viso vartotojų: {stats['total_users']}")
    print(f"  Neapdorotų transakcijų: {stats['pending_transactions']}")
    print(f"  Grandinė valid: {'Taip' if stats['chain_valid'] else 'Ne'}")
    
    if stats['total_transactions'] > 0:
        processing_rate = (stats['total_transactions'] / 
                          (stats['total_blocks'] - 1) * 100) if stats['total_blocks'] > 1 else 0
        print(f"  Apdorojimo greitis: ~{stats['total_transactions']/(stats['total_blocks']-1):.0f} tx/blokas")
    
    print("="*70)
    
    # 7. Rodome grandinę
    blockchain.print_chain()
    
    # 8. Rodome kelis vartotojų balansus
    print("\n" + "="*70)
    print("VARTOTOJŲ BALANSAI (Atsitiktiniai 10)")
    print("="*70)
    
    sample_users = random.sample(users, min(10, len(users)))
    for i, user in enumerate(sample_users):
        print(f"{i+1}. {user.name}: {user.balance:.2f}")
    
    print("="*70)
    
    print("\n" + "="*70)
    print("BLOCKCHAIN SIMULIACIJA BAIGTA")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma nutraukta vartotojo")
    except Exception as e:
        print(f"\n\nKlaida: {e}")
        import traceback
        traceback.print_exc()
