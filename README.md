# Car Simulation using Pygame and NEAT

## Description

The Car Simulation project is an exciting and interactive endeavor that combines the power of Pygame, a popular Python library for game development, with NEAT (NeuroEvolution of Augmenting Topologies), a genetic algorithm for evolving artificial neural networks. The project aims to create a virtual environment where cars can navigate a dynamic track, learning to improve their driving skills through the process of artificial evolution.

In this simulation, each car is controlled by a neural network, which initially has random connections and weights. The cars start with minimal driving abilities and struggle to move effectively around the track. However, using NEAT, the neural networks undergo evolutionary processes such as mutation and crossover to generate new networks with improved driving strategies. Over time, the cars learn to adapt and make decisions based on sensory inputs, such as their proximity to track boundaries and obstacles.

Pygame serves as the ideal platform to visualize this dynamic environment, offering graphics and user interactions to create an engaging and visually appealing car simulation. The project provides real-time rendering, allowing users to watch the cars' progress and learn from their interactions with the environment.

## Key Components

### Track Design
Creating an intricate and challenging track layout using Pygame's drawing capabilities.

### Car Physics
Implementing realistic car physics to model acceleration, deceleration, and steering actions.

### Neural Network Training
Utilizing NEAT to evolve the car's neural networks, optimizing their decision-making abilities.

### User Interactivity
Allowing users to control the simulation, pause, or reset the learning process for experimentation.

### Performance Evaluation
Implementing a fitness function to evaluate the performance of each car based on track completion and time taken.

## Getting Started

### Prerequisites
Ensure you have Python installed on your machine along with the required libraries: Pygame and NEAT. You can install them using pip:

```bash
pip install pygame
pip install neat-python


### Running the Simulation
Clone this repository and run the `car_simulation.py` script to start the car simulation:

'''bash
python car_simulation.py
