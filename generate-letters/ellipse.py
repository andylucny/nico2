import numpy as np
from scipy.integrate import quad
from scipy.optimize import root_scalar

def element(theta, A, B):
    dx_dtheta = -A * np.sin(theta)
    dy_dtheta = B * np.cos(theta)
    return np.sqrt(dx_dtheta**2 + dy_dtheta**2)

def length_of_perimeter(A, B):
    # Integrácia od 0 po pi (horná polovica)
    return quad(element, 0, np.pi, args=(A, B))[0]

def angle_for_length(s_target, A, B, total_length):
    # Nájde theta, pri ktorom je dĺžka oblúka rovná s_target
    def func(theta):
        result, _ = quad(element, 0, theta, args=(A, B))
        return result - s_target
    res = root_scalar(func, bracket=[0, np.pi], method='brentq')
    return res.root

def generate_perimeter(A, B, N):
    total_length = length_of_perimeter(A, B)
    krok = total_length / (N - 1)

    body = []
    for i in range(N):
        s = i * krok
        theta = angle_for_length(s, A, B, total_length)
        x = A * np.cos(theta)
        y = B * np.sin(theta)
        body.append((y, x))
    
    return body

if __name__ == "__main__":

    import matplotlib.pyplot as plt
    
    # Príklad použitia
    A = 15
    B = 7.5
    N = 30
    body = generate_perimeter(B, A, N)

    # Vykreslenie
    x_vals, y_vals = zip(*body)
    plt.figure(figsize=(6, 4))
    plt.plot(x_vals, y_vals, 'o-', label='Rovnomerne rozmiestnené body')
    plt.gca().set_aspect('equal')
    plt.grid(True)
    plt.title('Rovnomerne vzdialené body na polovici elipsy')
    plt.legend()
    plt.show()
