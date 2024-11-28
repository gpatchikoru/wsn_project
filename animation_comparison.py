
import numpy as np
import random
import math
import matplotlib.pyplot as plt

xm, ym = 100, 100        
n = 100                  
sinkx, sinky = 50, 50      
Eo = 0.5                  
Eelec = 50 * 10**-9      
Eamp = 100 * 10**-12     
k = 2000                  
p = 0.1                    

class ImprovedPEGASIS:
    def __init__(self):
        self.xm, self.ym = xm, ym
        self.n = n
        self.sinkx, self.sinky = sinkx, sinky
        self.Eo = Eo
        self.Eelec = Eelec
        self.Eamp = Eamp
        self.k = k
        self.aggregation_cost = 0.1  

    def initialize_nodes(self):
        """Initialize sensor nodes with enhanced attributes"""
        nodes = np.zeros(self.n, dtype=[
            ('id', int),          
            ('x', float),         
            ('y', float),         
            ('E', float),         
            ('cond', int),        
            ('next', int),      
            ('prev', int),       
            ('data', float),      
            ('dts', float)        
        ])
        for i in range(self.n):
            x = random.uniform(0, self.xm)
            y = random.uniform(0, self.ym)
            dist_to_sink = math.sqrt((x - self.sinkx)**2 + (y - self.sinky)**2)
            nodes[i] = (i + 1, x, y, self.Eo, 1, 0, 0, 0, dist_to_sink)
        
        return nodes

    def distance(self, node1, node2):
        return math.sqrt((node1['x'] - node2['x'])**2 + (node1['y'] - node2['y'])**2)

    def build_chain(self, nodes):
        alive_nodes = [i for i in range(self.n) if nodes[i]['cond'] == 1]
        if not alive_nodes:
            return nodes, []
        start_node = max(alive_nodes, key=lambda i: nodes[i]['dts'])
        chain = [start_node]
        unused_nodes = set(alive_nodes) - {start_node}
        current = start_node
        while unused_nodes:
            next_node = min(unused_nodes, 
                          key=lambda i: self.distance(nodes[current], nodes[i]))
            nodes[current]['next'] = next_node + 1
            nodes[next_node]['prev'] = current + 1
            
            chain.append(next_node)
            unused_nodes.remove(next_node)
            current = next_node

        return nodes, chain

    def transmit_data(self, nodes, sender, receiver, leader=False):
        if nodes[sender]['cond'] == 0:
            return nodes, False
        d = self.distance(nodes[sender], nodes[receiver])
        energy_aggregation = self.k * self.Eelec * self.aggregation_cost
        energy_tx = self.k * (self.Eelec + self.Eamp * d * d)
        energy_rx = self.k * self.Eelec + energy_aggregation
        nodes[sender]['E'] -= energy_tx
        if not leader:  
            nodes[receiver]['E'] -= energy_rx
        if nodes[sender]['E'] <= 0:
            nodes[sender]['cond'] = 0
            return nodes, False
        if not leader and nodes[receiver]['E'] <= 0:
            nodes[receiver]['cond'] = 0
            return nodes, False

        return nodes, True

    def run_simulation(self):
        nodes = self.initialize_nodes()
        results = []
        round_num = 0

        while np.sum(nodes['cond']) > 0:
            if round_num % 20 == 0:
                nodes, chain = self.build_chain(nodes)
                if not chain:  
                    break
            leader_idx = chain[round_num % len(chain)]
            collected_data = 0
            current = chain[0]
            while current != leader_idx:
                next_node = nodes[current]['next'] - 1
                nodes, success = self.transmit_data(nodes, current, next_node)
                if success:
                    collected_data += 1
                current = next_node
            if nodes[leader_idx]['cond'] == 1:
                dist_to_bs = math.sqrt((nodes[leader_idx]['x'] - self.sinkx)**2 + 
                                     (nodes[leader_idx]['y'] - self.sinky)**2)
                energy_to_bs = self.k * (self.Eelec + self.Eamp * dist_to_bs * dist_to_bs)
                nodes[leader_idx]['E'] -= energy_to_bs
                
                if nodes[leader_idx]['E'] <= 0:
                    nodes[leader_idx]['cond'] = 0
            alive_nodes = np.sum(nodes['cond'])
            results.append((round_num, alive_nodes, collected_data))
            round_num += 1

        return results

def run_leach():
    """LEACH Protocol Implementation"""
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
                distances = [np.sqrt((node['x'] - ch['x'])**2 + (node['y'] - ch['y'])**2) 
                           for ch in cluster_heads]
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

def run_direct():
    """Direct Transmission Protocol Implementation"""
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

def run_mte():
    """Minimum Transmission Energy Protocol Implementation"""
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

def find_half_death_round(nodes):
    """Calculate round when 50% of nodes die"""
    half_nodes = n / 2
    for i, alive_nodes in enumerate(nodes):
        if alive_nodes <= half_nodes:
            return i
    return len(nodes)

def run_comparison():
    """Run comprehensive protocol comparison"""
    print("\nRunning protocol comparison...")
    print("Running LEACH protocol...")
    leach_results = run_leach()
    
    print("Running Direct protocol...")
    direct_results = run_direct()
    
    print("Running MTE protocol...")
    mte_results = run_mte()
    
    print("Running PEGASIS protocol...")
    pegasis = ImprovedPEGASIS()
    pegasis_results = pegasis.run_simulation()
    leach_rounds, leach_nodes = zip(*leach_results)
    direct_rounds, direct_nodes = zip(*direct_results)
    mte_rounds, mte_nodes = zip(*mte_results)
    pegasis_rounds, pegasis_nodes, _ = zip(*pegasis_results)
    plt.figure(figsize=(12, 6))
    plt.plot(leach_rounds, leach_nodes, 'b-', label='LEACH', linewidth=2)
    plt.plot(direct_rounds, direct_nodes, 'g-', label='Direct', linewidth=2)
    plt.plot(mte_rounds, mte_nodes, 'r-', label='MTE', linewidth=2)
    plt.plot(pegasis_rounds, pegasis_nodes, 'y-', label='PEGASIS', linewidth=2)
    
    plt.xlabel('Round Number')
    plt.ylabel('Number of Alive Nodes')
    plt.title('Comparison of WSN Protocols')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Save and show plot
    plt.savefig('protocol_comparison.png')
    plt.show()
    
    # Print statistics
    print("\nNetwork Lifetime (rounds):")
    print(f"LEACH: {len(leach_rounds)}")
    print(f"Direct: {len(direct_rounds)}")
    print(f"MTE: {len(mte_rounds)}")
    print(f"PEGASIS: {len(pegasis_rounds)}")
    
    print("\nRound when 50% of nodes die:")
    print(f"LEACH: {find_half_death_round(leach_nodes)}")
    print(f"Direct: {find_half_death_round(direct_nodes)}")
    print(f"MTE: {find_half_death_round(mte_nodes)}")
    print(f"PEGASIS: {find_half_death_round(pegasis_nodes)}")

if __name__ == "__main__":
    run_comparison()