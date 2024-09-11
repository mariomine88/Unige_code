import numpy as np

# gennero una matrice di dimensione size x size con valori dati da value_range
def generate_matrix(size, value_range):
    return np.random.choice(value_range, size=(size, size))

def modify_matrix(C):
    C[2, 8] += 1 
    return C

def MCMatrixMultiplicationVerifier(A, B, C, k):
    n = A.shape[0] # dimensione delle matrici
    for _ in range(k):
        # genero un vettore casuale di 0 e 1 di dimensione n
        r = np.random.randint(2, size=(n, 1)) 
        # calcolo i prodotti matriciali
        s = np.dot(B, r)
        t = np.dot(A, s)
        u = np.dot(C, r)
        #controllo se i due risultati sono uguali
        if not np.array_equal(t, u):
            return "AB ≠ C"
    return "probably AB = C"

def experiment(k_values, trials=100):
    results = {k: {'probably AB = C': 0, 'AB ≠ C': 0} for k in k_values}
    for _ in range(trials):
        A = generate_matrix(100, [-2, -1, 0, 1, 2]) # Generate a random matrix A
        B = generate_matrix(100, [-2, -1, 0, 1, 2]) # Generate a random matrix B
        C = np.dot(A, B) # calcolo C
        C = modify_matrix(C)
        for k in k_values:
            # faccio il test per ogni k
            verdict = MCMatrixMultiplicationVerifier(A, B, C, k) 
            results[k][verdict] += 1
    return results

k_values = [5, 10, 20]
results = experiment(k_values)
print(f"Results for k values {k_values}: {results}")