import numpy as np
import random
import matplotlib.pyplot as plt

# Network Parameters
xm, ym = 100, 100  # Field dimensions
n = 100  # Number of nodes
sinkx, sinky = 50, 50  # Sink coordinates
Eo = 0.5  # Initial energy of nodes
Eelec = 50 * 10**-9  # Energy for running circuitry
Eamp = 50 * 10**-12  # Optimized amplification energy for LEACH
k = 2000  # Data packet size
p = 0.1  # Increased percentage of cluster heads for LEACH

# Optimized LEACH Protocol Simulation
def run_leach():
    nodes = np.array([
        (i, random.randint(0, xm), random.randint(0, ym), Eo, 0, 0, 1, 0, 
         np.sqrt((random.randint(0, xm)-sinkx)**2 + (random.randint(0, ym)-sinky)**2), 0)
        for i in range(1, n + 1)
    ], dtype=[
        ('id', int), ('x', int), ('y', int), ('E', float),
        ('role', int), ('cluster', int), ('cond', int),
        ('rop', int), ('dts', float), ('tel', int)
    ])
    
    results = []
    rounds = 0
    while np.sum(nodes['cond']) > 0:
        cluster_heads = []
        # Select cluster heads
        for node in nodes:
            if node['cond'] == 1 and random.uniform(0, 1) <= p:
                node['role'] = 1
                cluster_heads.append(node)

        # Assign nodes to nearest cluster head
        for node in nodes:
            if node['cond'] == 1 and node['role'] == 0:
                distances = [np.sqrt((node['x'] - ch['x'])**2 + (node['y'] - ch['y'])**2) for ch in cluster_heads]
                if distances:
                    min_distance = np.argmin(distances)
                    energy_spent = Eelec * k + (Eamp / 2) * k * distances[min_distance]**2  # Reduced amplification energy
                    node['E'] -= energy_spent
                    if node['E'] <= 0:
                        node['cond'] = 0

        # Cluster head energy dissipation
        for ch in cluster_heads:
            if ch['cond'] == 1:
                ch['E'] -= Eelec * k
                if ch['E'] <= 0:
                    ch['cond'] = 0

        results.append((rounds, np.sum(nodes['cond'])))
        rounds += 1
        
        # Reset roles for next round
        nodes['role'] = 0
        
    return results

# Direct Protocol Simulation
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

# MTE Protocol Simulation
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
                # Find nearest neighbor
                distances = []
                for other_node in nodes:
                    if other_node['id'] != node['id'] and other_node['cond'] == 1:
                        dist = np.sqrt((node['x'] - other_node['x'])**2 + 
                                     (node['y'] - other_node['y'])**2)
                        distances.append((dist, other_node))
                
                if distances:
                    next_hop = min(distances, key=lambda x: x[0])[1]
                    # Energy for transmission to next hop
                    dist_to_hop = np.sqrt((node['x'] - next_hop['x'])**2 + 
                                        (node['y'] - next_hop['y'])**2)
                    energy_spent = Eelec * k + Eamp * k * dist_to_hop**2
                    node['E'] -= energy_spent
                    
                    # Energy for next hop to sink
                    energy_spent_next = Eelec * k + Eamp * k * next_hop['dts']**2
                    next_hop['E'] -= energy_spent_next
                else:
                    # Direct transmission to sink if no neighbors
                    energy_spent = Eelec * k + Eamp * k * node['dts']**2
                    node['E'] -= energy_spent
                
                if node['E'] <= 0:
                    node['cond'] = 0

        results.append((rounds, np.sum(nodes['cond'])))
        rounds += 1
        
    return results

# Run simulations
print("Running LEACH simulation...")
leach_results = run_leach()
print("Running Direct simulation...")
direct_results = run_direct()
print("Running MTE simulation...")
mte_results = run_mte()

# Create comparison plot
leach_rounds, leach_nodes = zip(*leach_results)
direct_rounds, direct_nodes = zip(*direct_results)
mte_rounds, mte_nodes = zip(*mte_results)

plt.figure(figsize=(12, 6))
plt.plot(leach_rounds, leach_nodes, 'b-', label='LEACH (Optimized)', linewidth=2)
plt.plot(direct_rounds, direct_nodes, 'g-', label='Direct', linewidth=2)
plt.plot(mte_rounds, mte_nodes, 'r-', label='MTE', linewidth=2)

plt.xlabel('Round Number')
plt.ylabel('Number of Alive Nodes')
plt.title('Comparison of LEACH (Optimized) vs Direct vs MTE Protocols')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()



plt.show()

# Print statistics
print("\nNetwork Lifetime (rounds):")
print(f"LEACH: {len(leach_rounds)}")
print(f"Direct: {len(direct_rounds)}")
print(f"MTE: {len(mte_rounds)}")

def find_half_death_round(nodes):
    half_nodes = n / 2
    for i, alive_nodes in enumerate(nodes):
        if alive_nodes <= half_nodes:
            return i
    return len(nodes)

print("\nRound when 50% of nodes die:")
print(f"LEACH: {find_half_death_round(leach_nodes)}")
print(f"Direct: {find_half_death_round(direct_nodes)}")
print(f"MTE: {find_half_death_round(mte_nodes)}")
