#!/usr/bin/env python
# coding: utf-8

import numpy as np
import math
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Network Establishment Parameters
xm, ym = 100, 100  # Field dimensions
n = 100  # Number of nodes
sinkx, sinky = 0, -100  # Sink coordinates
Eo = 0.5  # Initial energy (J)
Eelec = 50 * 10 ** -9  # Circuitry energy (J/bit)
Eamp = 100 * 10 ** -12  # Amplification energy (J/bit/m^2)
k = 2000  # Packet size (bits)
p = 0.05  # Cluster head percentage

# Function to initialize nodes
def initialize_nodes():
    return np.array([
        (i, random.randint(0, xm), random.randint(0, ym), Eo, 0, 0, 1, 0,
         math.sqrt((random.randint(0, xm) - sinkx)**2 + (random.randint(0, ym) - sinky)**2), 0)
        for i in range(1, n + 1)
    ], dtype=[
        ('id', int), ('x', int), ('y', int), ('E', float), ('role', int),
        ('cluster', int), ('cond', int), ('rop', int), ('dts', float), ('tel', int)
    ])

# LEACH protocol
def leach_protocol():
    nodes = initialize_nodes()
    cluster_history = []
    rounds = 0

    while rounds < 100 and np.sum(nodes['cond']) > 0:
        nodes["role"] = 0
        cluster_heads = []
        
        # Select cluster heads
        for node in nodes:
            if node['cond'] == 1 and random.uniform(0, 1) <= p:
                node['role'] = 1
                cluster_heads.append(node)

        # Assign nodes to nearest cluster head
        for node in nodes:
            if node['cond'] == 1 and node['role'] == 0:
                distances = [
                    math.sqrt((node['x'] - ch['x'])**2 + (node['y'] - ch['y'])**2)
                    for ch in cluster_heads
                ]
                if distances:
                    min_dist = np.argmin(distances)
                    node['cluster'] = cluster_heads[min_dist]['id']

        cluster_history.append((rounds, nodes['cluster'].copy()))
        rounds += 1

    return nodes, cluster_history

# Function to generate animations for a protocol
def generate_animation(protocol_name, cluster_history, output_file):
    fig, ax = plt.subplots(figsize=(8, 8))

    def update(frame):
        round_num, clusters = cluster_history[frame]
        ax.clear()
        ax.scatter(nodes['x'], nodes['y'], c=clusters, cmap='rainbow', s=100)
        ax.set_title(f"{protocol_name} - Round {round_num}")
        ax.set_xlim(0, xm)
        ax.set_ylim(0, ym)
        ax.grid(True)

    ani = animation.FuncAnimation(fig, update, frames=len(cluster_history), interval=500, blit=False)
    ani.save(output_file, writer='ffmpeg')
    plt.close(fig)

# Main
if __name__ == "__main__":
    # LEACH Protocol
    print("Generating LEACH animation...")
    nodes, leach_history = leach_protocol()
    generate_animation("LEACH", leach_history, "leach_animation.mp4")

    # Direct Protocol
    print("Generating Direct animation...")
    nodes, direct_history = leach_protocol()  # Replace with Direct protocol logic
    generate_animation("Direct", direct_history, "direct_animation.mp4")

    # MTE Protocol
    print("Generating MTE animation...")
    nodes, mte_history = leach_protocol()  # Replace with MTE protocol logic
    generate_animation("MTE", mte_history, "mte_animation.mp4")

    print("All animations have been saved.")
