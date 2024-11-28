import numpy as np
import random
import math

class ImprovedPEGASIS:
    def __init__(self, xm=100, ym=100, n=100, sinkx=50, sinky=50, Eo=0.5,
                 Eelec=50e-9, Eamp=100e-12, k=2000):
        self.xm = xm
        self.ym = ym
        self.n = n
        self.sinkx = sinkx
        self.sinky = sinky
        self.Eo = Eo
        self.Eelec = Eelec
        self.Eamp = Eamp
        self.k = k
        
    def initialize_nodes(self):
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
        distances_to_sink = [(i, nodes[i]['dts']) for i in range(self.n)]
        start_node_idx = max(distances_to_sink, key=lambda x: x[1])[0]
        chain = [start_node_idx]
        unused_nodes = set(range(self.n)) - {start_node_idx}
        current = start_node_idx
        while unused_nodes:
            min_dist = float('inf')
            next_node = None
            for i in unused_nodes:
                dist = self.distance(nodes[current], nodes[i])
                if dist < min_dist:
                    min_dist = dist
                    next_node = i
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
        energy_tx = self.k * (self.Eelec + self.Eamp * d * d)
        energy_rx = self.k * self.Eelec
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
    
    def run_simulation(self, max_rounds=1000):
        nodes = self.initialize_nodes()
        results = []
        round_num = 0
        while round_num < max_rounds and np.sum(nodes['cond']) > 0:
            if round_num % 20 == 0:
                nodes, chain = self.build_chain(nodes)
            leader_idx = round_num % self.n
            collected_data = 0
            current = chain[0]
            while current != leader_idx:
                next_node = nodes[current]['next'] - 1
                nodes, success = self.transmit_data(nodes, current, next_node)
                if success:
                    collected_data += 1
                current = next_node
            if nodes[leader_idx]['cond'] == 1:
                leader_node = nodes[leader_idx]
                dist_to_bs = math.sqrt((leader_node['x'] - self.sinkx)**2 + 
                                     (leader_node['y'] - self.sinky)**2)
                energy_to_bs = self.k * (self.Eelec + self.Eamp * dist_to_bs * dist_to_bs)
                nodes[leader_idx]['E'] -= energy_to_bs
                if nodes[leader_idx]['E'] <= 0:
                    nodes[leader_idx]['cond'] = 0
            alive_nodes = np.sum(nodes['cond'])
            results.append((round_num, alive_nodes, collected_data))
            round_num += 1
        return results

def run_pegasis_simulation():
    pegasis = ImprovedPEGASIS()
    results = pegasis.run_simulation()
    return results

if __name__ == "__main__":
    results = run_pegasis_simulation()
    rounds, alive_nodes, data_collected = zip(*results)
    print("\nPEGASIS Simulation Results:")
    print(f"Network lifetime: {len(rounds)} rounds")
    print(f"Average nodes alive: {sum(alive_nodes)/len(rounds):.2f}")
    print(f"Total data collected: {sum(data_collected)}")
