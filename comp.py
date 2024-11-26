#!/usr/bin/env python
# coding: utf-8

import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Network Parameters
xm, ym = 100, 100  # Field dimensions
n = 100  # Number of nodes
sinkx, sinky = 50, 50  # Sink coordinates
Eo = 0.5  # Initial energy of nodes
Eelec = 50 * 10**-9  # Energy for running circuitry
Eamp = 100 * 10**-12  # Energy for amplification
k = 2000  # Data packet size
p = 0.05  # Percentage of cluster heads

# LEACH Protocol Simulation
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
        for node in nodes:
            if node['cond'] == 1 and random.uniform(0, 1) <= p:
                node['role'] = 1
                cluster_heads.append(node)

        for node in nodes:
            if node['cond'] == 1 and node['role'] == 0:
                distances = [np.sqrt((node['x'] - ch['x'])**2 + (node['y'] - ch['y'])**2) for ch in cluster_heads]
                if distances:
                    min_distance = np.argmin(distances)
                    energy_spent = Eelec * k + Eamp * k * distances[min_distance]**2
                    node['E'] -= energy_spent
                    if node['E'] <= 0:
                        node['cond'] = 0

        for ch in cluster_heads:
            if ch['cond'] == 1:
                ch['E'] -= Eelec * k
                if ch['E'] <= 0:
                    ch['cond'] = 0

        results.append((rounds, np.sum(nodes['cond'])))
        rounds += 1
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

# Run simulations
print('running leach')
leach_results = run_leach()
print('running direct')
direct_results = run_direct()
print('running mte')
mte_results = run_mte()

leach_rounds, leach_nodes = zip(*leach_results)
direct_rounds, direct_nodes = zip(*direct_results)
mte_rounds, mte_nodes = zip(*mte_results)

# Create figure for animation
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, max(max(leach_rounds), max(direct_rounds), max(mte_rounds)))
ax.set_ylim(0, n)
ax.set_xlabel('Round Number')
ax.set_ylabel('Number of Alive Nodes')
ax.set_title('Comparison of LEACH, Direct, and MTE Protocols')

leach_line, = ax.plot([], [], 'b-', label='LEACH', linewidth=2)
direct_line, = ax.plot([], [], 'g-', label='Direct', linewidth=2)
mte_line, = ax.plot([], [], 'r-', label='MTE', linewidth=2)

ax.legend()

# Update function for animation
def update(frame):
    leach_x, leach_y = leach_rounds[:frame], leach_nodes[:frame]
    direct_x, direct_y = direct_rounds[:frame], direct_nodes[:frame]
    mte_x, mte_y = mte_rounds[:frame], mte_nodes[:frame]
    
    leach_line.set_data(leach_x, leach_y)
    direct_line.set_data(direct_x, direct_y)
    mte_line.set_data(mte_x, mte_y)
    return leach_line, direct_line, mte_line

# Animate and save
ani = FuncAnimation(fig, update, frames=len(leach_rounds), repeat=False, blit=True)
ani.save('comparison_animation.mp4', writer='ffmpeg', fps=30)
plt.show()
