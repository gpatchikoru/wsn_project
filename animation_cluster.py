import numpy as np
import math
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

xm, ym = 100, 100
n = 100
sinkx, sinky = 0, -100
Eo = 0.5
Eelec = 50 * 10**-9
Eamp = 100 * 10**-12
k = 2000
p = 0.05

def initialize_nodes():
    nodes = np.zeros(n, dtype=[
        ('id', int), ('x', int), ('y', int), ('E', float), ('role', int),
        ('cluster', int), ('cond', int), ('rop', int), ('dts', float), ('tel', int)
    ])
    
    for i in range(n):
        x = random.randint(0, xm)
        y = random.randint(0, ym)
        distance_to_sink = math.sqrt((x - sinkx)**2 + (y - sinky)**2)
        nodes[i] = (i + 1, x, y, Eo, 0, 0, 1, 0, distance_to_sink, 0)
    
    return nodes

def leach_protocol():
    nodes = initialize_nodes()
    cluster_history = []
    rounds = 0
    
    while rounds < 100 and np.sum(nodes['cond']) > 0:
        nodes['role'] = 0
        nodes['cluster'] = 0
        
        active_nodes = nodes[nodes['cond'] == 1]
        cluster_heads = active_nodes[np.random.random(len(active_nodes)) < p]
        
        if len(cluster_heads) > 0:
            nodes['role'][cluster_heads['id'] - 1] = 1
            
            for node in nodes[nodes['cond'] == 1]:
                if node['role'] == 0:
                    distances = np.sqrt(
                        (node['x'] - cluster_heads['x'])**2 + 
                        (node['y'] - cluster_heads['y'])**2
                    )
                    nearest_ch = cluster_heads[np.argmin(distances)]
                    node['cluster'] = nearest_ch['id']
        
        cluster_history.append((rounds, nodes['cluster'].copy()))
        rounds += 1
    
    return nodes, cluster_history

def generate_animation(protocol_name, cluster_history, output_file):
    fig, ax = plt.subplots(figsize=(10, 10))
    
    def update(frame):
        ax.clear()
        round_num, clusters = cluster_history[frame]
        scatter = ax.scatter(nodes['x'], nodes['y'], 
                           c=clusters, cmap='tab20', 
                           s=100, alpha=0.6)
        ax.scatter(sinkx, sinky, c='red', marker='s', s=200, label='Base Station')
        ax.set_title(f"{protocol_name} Protocol - Round {round_num}", pad=20)
        ax.set_xlabel("X-coordinate (m)")
        ax.set_ylabel("Y-coordinate (m)")
        ax.set_xlim(-10, xm + 10)
        ax.set_ylim(sinky - 10, ym + 10)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        return scatter,

    ani = animation.FuncAnimation(fig, update, frames=len(cluster_history), 
                                interval=500, blit=True)
    
    writers = ['ffmpeg', 'pillow', 'imagemagick']
    for writer in writers:
        try:
            if writer == 'ffmpeg':
                output = output_file
            else:
                output = output_file.replace('.mp4', '.gif')
            print(f"Attempting to save animation using {writer}...")
            ani.save(output, writer=writer)
            print(f"Successfully saved animation as {output}")
            break
        except Exception as e:
            print(f"Could not save using {writer}: {str(e)}")
            continue
    
    plt.close(fig)

if __name__ == "__main__":
    output_dir = "animations"
    os.makedirs(output_dir, exist_ok=True)
    print("\nSimulating LEACH protocol...")
    nodes, leach_history = leach_protocol()
    generate_animation("LEACH", leach_history, 
                      os.path.join(output_dir, "leach_animation.mp4"))
