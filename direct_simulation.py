import numpy as np
import random

xm, ym = 100, 100
n = 100
sinkx, sinky = 50, 50
Eo = 0.5
Eelec = 50 * 10**-9
Eamp = 100 * 10**-12
k = 2000

def run_direct():
    nodes = np.array([
        (i, random.randint(0, xm), random.randint(0, ym), Eo, 1, 0, 
         np.sqrt((random.randint(0, xm)-sinkx)**2 + (random.randint(0, ym)-sinky)**2))
        for i in range(1, n + 1)
    ], dtype=[
        ('id', int), ('x', int), ('y', int), ('E', float), 
        ('cond', int), ('rop', int), ('dts', float)
    ])
    
    results = []
    rounds = 0
    while np.sum(nodes['cond']) > 0:
        for node in nodes:
            if node['cond'] == 1:
                energy_spent = Eelec * k + Eamp * k * node['dts']**2
                node['E'] -= energy_spent
                if node['E'] <= 0:
                    node['cond'] = 0

        results.append((rounds, np.sum(nodes['cond'])))
        rounds += 1
        
    return results

if __name__ == "__main__":
    print("Running Direct simulation...")
    results = run_direct()
    print(f"Simulation completed with {len(results)} rounds.")
