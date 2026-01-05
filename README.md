# Supaprastinta Blockchain Implementacija

## Aprašymas

Ši programa yra supaprastintos blokų grandinės (blockchain) implementacija Python kalba, atitinkanti v0.1 ir v0.2 versijų reikalavimus. Programa imituoja realios blockchain sistemos veikimą su vartotojais, transakcijomis, Merkle Tree, Proof-of-Work kasimo mechanizmu ir decentralizuotu kasimo procesu.

**Versija:** v0.2  
**Data:** 2025-01-05  

---

## Funkcionalumas

### v0.1 Funkcijos (Centralizuota blockchain)

- **Vartotojų generavimas**: ~1000 vartotojų su atsitiktiniais balansais (100-1,000,000)
- **Transakcijų generavimas**: ~10,000 transakcijų tarp vartotojų
- **Blokų struktūra**: 
  - Antraštė (Header): prev_block_hash, timestamp, version, merkle_root, nonce, difficulty_target
  - Turinys (Body): transakcijų sąrašas
- **Proof-of-Work kasimas**: Hash'uojama antraštė, kol hash prasideda "000..."
- **Genesis blokas**: Automatinis pirminio bloko sukūrimas
- **Transakcijų apdorojimas**: Balansų atnaujinimas po kiekvieno bloko
- **Savadarbė hash funkcija**: Naudojama SHA-256
- **Vizualus išvedimas**: Gražus progresas ir statistika konsolėje

### v0.2 Funkcijos (Decentralizuota blockchain)

- **Merkle Tree**: Pilna Merkle Tree implementacija su Merkle Root Hash
- **Transakcijų validacija**:
  - Balanso tikrinimas (siuntėjas negali siųsti daugiau, nei turi)
  - Transaction ID tikrinimas (hash teisingumas)
  - Siuntėjo/gavėjo egzistavimo tikrinimas
  - Teigiamos sumos tikrinimas
- **Decentralizuotas kasimas**:
  - Generuojama 5 kandidatiniai blokai (~100 tx kiekviename)
  - Kasami ribotą laiką (5s per bloką)
  - Jei nepavyksta - bandoma su dvigubu laiku
  - Imituojamas konkurencinis kasimas
- **Grandinės validacija**: Patikrina visus blokus ir jų ryšius

---

## Projekto Struktūra

```
blockchain-project/
│
├── blockchain.py          # Pagrindinės klasės (User, Transaction, Block, Blockchain)
├── main.py               # Pagrindinis vykdomasis failas
└── README.md             # Dokumentacija
```

---

## Klasių Struktūra

### 1. `User` klasė
Reprezentuoja blockchain vartotoją.

**Atributai:**
- `name` (str): Vartotojo vardas
- `public_key` (str): Viešasis raktas (64 hex simboliai)
- `balance` (float): Vartotojo balansas

**Metodai:**
- `__init__(name, public_key, balance)`: Konstruktorius
- `to_dict()`: Konvertuoja į dictionary formatą

### 2. `Transaction` klasė
Reprezentuoja transakciją tarp dviejų vartotojų.

**Atributai:**
- `sender` (str): Siuntėjo viešasis raktas
- `receiver` (str): Gavėjo viešasis raktas
- `amount` (float): Pervedama suma
- `transaction_id` (str): Unikalus transakcijos identifikatorius (hash)

**Metodai:**
- `__init__(sender, receiver, amount)`: Konstruktorius
- `_calculate_hash()`: Apskaičiuoja transakcijos hash
- `is_valid(users_dict)`: Patikrina transakcijos validumą
- `to_dict()`: Konvertuoja į dictionary formatą

### 3. `MerkleTree` klasė
Implementuoja Merkle Tree duomenų struktūrą.

**Atributai:**
- `transactions` (List[Transaction]): Transakcijų sąrašas
- `tree` (List[List[str]]): Merkle Tree lygiai
- `root` (str): Merkle Root Hash

**Metodai:**
- `__init__(transactions)`: Konstruktorius, sukuria medį
- `_build_tree()`: Stato Merkle Tree
- `get_root()`: Grąžina Merkle Root hash

**Veikimo principas:**
1. Kiekvienos transakcijos hash - pirmasis lygis
2. Poruojami ir hash'uojami kol lieka vienas (root)
3. Jei nelyginis skaičius - dubliuojamas paskutinis

### 4. `BlockHeader` klasė
Reprezentuoja bloko antraštę.

**Atributai:**
- `prev_block_hash` (str): Ankstesnio bloko hash
- `timestamp` (float): Unix timestamp
- `version` (str): Bloko versija
- `merkle_root` (str): Merkle root hash
- `nonce` (int): Proof-of-Work nonce
- `difficulty_target` (int): Kasimo sudėtingumas

### 5. `Block` klasė
Pilna bloko implementacija.

**Atributai:**
- Visi `BlockHeader` atributai
- `transactions` (List[Transaction]): Transakcijų sąrašas
- `merkle_tree` (MerkleTree): Merkle Tree objektas
- `block_hash` (str): Bloko hash

**Metodai:**
- `__init__(prev_block_hash, transactions, version, difficulty_target)`: Konstruktorius
- `get_header()`: Grąžina BlockHeader objektą
- `calculate_hash()`: Apskaičiuoja bloko hash pagal antraštę
- `mine_block(max_time, max_attempts)`: Kasa bloką (PoW)
- `to_dict()`: Konvertuoja į dictionary formatą

**Kasimo algoritmas:**
```python
while True:
    hash = calculate_hash()
    if hash.startswith("000"):  # difficulty = 3
        return True
    if time_exceeded or attempts_exceeded:
        return False
    nonce += 1
```

### 6. `Blockchain` klasė
Valdžia visą blokų grandinę.

**Atributai:**
- `chain` (List[Block]): Blokų grandinė
- `difficulty` (int): Kasimo sudėtingumas
- `users` (Dict[str, User]): Vartotojų žodynas
- `pending_transactions` (List[Transaction]): Laukiančios transakcijos

**Metodai:**
- `__init__(difficulty)`: Konstruktorius, sukuria Genesis bloką
- `_create_genesis_block()`: Sukuria pirminį bloką
- `add_user(user)`: Prideda vartotoją
- `add_transaction(transaction)`: Prideda transakciją
- `create_candidate_blocks(num, tx_per_block)`: Kuria kandidatinius blokus
- `mine_and_add_block(max_time, max_attempts)`: Kasa ir prideda bloką
- `is_chain_valid()`: Validuoja visą grandinę
- `print_chain()`: Gražiai išveda grandinę
- `get_statistics()`: Grąžina statistiką

## AI Pagalbos Naudojimas

### Kur buvo pasitelkta AI pagalba:

1. **Merkle Tree Algoritmas** (v0.2)
   - AI padėjo suprasti Merkle Tree veikimo principą
   - Pateikė pavyzdinį kodą medžio statymui
   - Paaiškino, kaip tvarkyti nelyginį transakcijų skaičių

3. **Kodo Struktūros Patobulinimai**
   - AI pasiūlė išskaidyti `mine_and_add_block` į mažesnius metodus
   - Padėjo optimizuoti transakcijų validaciją
   - Pateikė type hints naudojimo gaires

4. **Dokumentacijos Šablonas**
   - AI padėjo sukurti README.md struktūrą
   - Pateikė pavyzdžių, kaip aprašyti klases ir metodus

---

## Licencija

Šis projektas sukurtas edukaciniais tikslais VU BGT kursui.
