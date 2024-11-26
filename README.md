# Wireless Sensor Networks Simulation with LEACH, Direct, and MTE Protocols

This project simulates and compares three protocols for wireless sensor networks: LEACH, Direct, and MTE. The simulations evaluate the energy efficiency and node lifetimes under these protocols. Additionally, the project includes animations to visualize cluster formation and lifetime comparisons.

## Features

### Protocols Simulated:

- **LEACH** (Low-Energy Adaptive Clustering Hierarchy)
- **Direct Transmission**
- **MTE** (Minimum Transmission Energy)

### Visualizations:

- Cluster formation and progression for each protocol.
- Lifetime comparison between LEACH, Direct, and MTE protocols.

### Output:

- Number of alive nodes per round for each protocol.
- Animations showing clustering dynamics and protocol comparisons.

## Repository Structure

- `leach_simulation.py`: Simulates the LEACH protocol.
- `direct_simulation.py`: Simulates the Direct protocol.
- `mte_simulation.py`: Simulates the MTE protocol.
- `animation_cluster.py`: Animates the cluster formation for LEACH, Direct, and MTE protocols.
- `animation_comparison.py`: Animates the lifetime comparison of LEACH, Direct, and MTE protocols.
- `requirements.txt`: Lists the required Python libraries.
- `README.md`: Documentation for the project.

## Requirements

To run the simulations and animations, ensure you have the following:

### Python 3.x

### Libraries:

- **NumPy**
- **Matplotlib**
- **FFMPEG** (for saving animations as videos)

Install the Python dependencies using:

```bash
pip install -r requirements.txt
```

## How to Run

### 1. Simulating Protocols

To simulate each protocol and display results:

#### LEACH:

```bash
python leach_simulation.py
```

#### Direct:

```bash
python direct_simulation.py
```

#### MTE:

```bash
python mte_simulation.py
```

Each simulation outputs the number of alive nodes per round and key statistics such as the round when 50% of nodes die.

### 2. Animating Cluster Formation

To visualize cluster formation and progression for the first 100 rounds:

```bash
python animation_cluster.py
```

This script generates an animation for LEACH, Direct, and MTE cluster dynamics and saves it as a video file (`cluster_animation.mp4`).

### 3. Animating Protocol Comparison

To compare the lifetime of the three protocols visually:

```bash
python animation_comparison.py
```

This script generates an animated line graph comparing the number of alive nodes per round for LEACH, Direct, and MTE protocols. The animation is saved as a video file (`comparison_animation.mp4`).

## Output

### 1. Simulations

Each protocol simulation provides:

- The total network lifetime in terms of rounds.
- The round at which 50% of nodes die.
- The progression of alive nodes per round.

### 2. Animations

- **Cluster Formation**: Visualizes how clusters form and change dynamically in LEACH, Direct, and MTE protocols.
- **Lifetime Comparison**: Displays the number of alive nodes over time, comparing the three protocols.

animations are saved as `.mp4` video files for clustering and for comparing in matplot .

## Key Observations

- **LEACH**: Uses cluster heads for energy-efficient communication, resulting in prolonged network lifetime.
- **Direct**: Sends data directly to the sink, which is simpler but less energy-efficient.
- **MTE**: Optimizes energy use by selecting the nearest hop for data transmission but may cause faster node depletion in critical areas.

## Customization

- Modify simulation parameters (e.g., number of nodes, area size, energy values) in each script for tailored experiments.
- Adjust the number of rounds for animations in `animation_cluster.py` and `animation_comparison.py`.

_Compares the alive node progression across LEACH, Direct, and MTE protocols._

## Notes

- Each simulation run produces slightly different results due to the use of random initial conditions and node placements.
- **FFMPEG** must be installed on your system to save animations as `.mp4` files. Install it via:
  ```bash
  sudo apt-get install ffmpeg  # For Ubuntu
  brew install ffmpeg          # For macOS
  ```
- Animations are optimized for 100 rounds but can be extended by adjusting the relevant loop parameters.
