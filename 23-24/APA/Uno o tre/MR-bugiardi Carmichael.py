def is_witness(a, n):
    # risciviamo n-1 come q*2^s
    q, s = n - 1, 0
    while q % 2 == 0:
        s += 1
        q //= 2
    
    # controlliamo se a^q % n == 1
    x = pow(a, q, n)
    if x == 1 or x == n - 1:
        return False 
    
    # controlliamo se a^(2^i * q) % n == n-1 per qualche i
    for _ in range(s - 1):
        x = pow(x, 2, n)
        if x == n - 1:
            return False 
    
    return True  # se supera i controlli sopra, a è un witness

# facciamo il test di Miller-Rabin
def find_MR_liars(n):
    liars = []
    for a in range(2, n-2):
        if not is_witness(a, n):
            liars.append(a)
    # aggiungiamo 1  e n-1 perche' sono sempre liars
    liars = [1] + liars
    liars.append(n-1) 
    return liars

# salviamo i risultati in un file
carmichael_numbers = [561, 1105, 1729, 2465, 2821, 6601, 8911]
with open('MR_liars_results.txt', 'w') as file:
    for n in carmichael_numbers:
        liars = find_MR_liars(n)
        file.write(f"MR_liars for {n}: {liars}\n")
        


