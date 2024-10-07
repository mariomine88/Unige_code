import random
from sympy import primerange
# Lista di numeri primi tra 2 e 400
primes = list(primerange(2, 400))

def generate_random_prime():
    # Campiona un numero primo a caso tra 2 e 400
    return random.choice(primes)

def hash_mod_p(s, p):
    # Converti la stringa binaria in un numero intero
    # e calcola modulo p e restituisci il risultato
    return int(s, 2) % p

def MCStringEqualityVerifier(a, b, trials=20):
    for _ in range(trials):
        p = generate_random_prime()
        if hash_mod_p(a, p) != hash_mod_p(b, p):
            return False  # Diverse
    return True  # Probabilmente uguali

# Esempio di utilizzo
a = '11111111111111111110'  # Stringa a
b = '11111111111111111111'  # Stringa b


result = MCStringEqualityVerifier(a, b)
print("Le stringhe sono", "probabilmente uguali" if result else "diverse")



