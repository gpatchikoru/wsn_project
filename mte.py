import numpy as np
import random

xm, ym = 100, 100
n = 100
sinkx, sinky = 50, 50
Eo = 0.5
Eelec = 50 * 10**-9
Eamp = 100 * 10**-12
k = 2000

def run_mte():
    nodes = np.array([
        (i, random.randint(0, xm), random.randint(0, ym), Eo, 1,
         np.sqrt((random.randint(0, xm)-sinkx)**2 + (random.randint(0, ym)-sinky)**2))
        for i in range(1, n + 1)
    ], dtype=[
        ('id', int), ('x', int), ('y', int), ('E', float), 
        ('cond', int), ('dts', float)
    ])
    
    results = []
    rounds = 0
    
    while np.sum(nodes['cond']) > 0:
        for node in nodes:
            if node['cond'] == 1:
                distances = []
                for other_node in nodes:
                    if other_node['id'] != node['id'] and other_node['cond'] == 1:
                        dist = np.sqrt((node['x'] - other_node['x'])**2 + 
                                     (node['y'] - other_node['y'])**2)
                        distances.append((dist, other_node))
                
                if distances:
                    next_hop = min(distances, key=lambda x: x[0])[1]
                    dist_to_hop = np.sqrt((node['x'] - next_hop['x'])**2 + 
                                        (node['y'] - next_hop['y'])**2)
                    energy_spent = Eelec * k + Eamp * k * dist_to_hop**2
                    node['E'] -= energy_spent
                    
                    energy_spent_next = Eelec * k + Eamp * k * next_hop['dts']**2
                    next_hop['E'] -= energy_spent_next
                else:
                    energy_spent = Eelec * k + Eamp * k * node['dts']**2
                    node['E'] -= energy_spent
                
                if node['E'] <= 0:
                    node['cond'] = 0

        results.append((rounds, np.sum(nodes['cond'])))
        rounds += 1
        
    return results

if __name__ == "__main__":
    print("Running MTE simulation...")
    results = run_mte()
    print(f"Simulation completed with {len(results)} rounds.")
