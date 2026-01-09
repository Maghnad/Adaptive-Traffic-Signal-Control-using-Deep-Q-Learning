import os
import sys
import random
import numpy as np
import traci
from collections import deque
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# --- 1. ENVIRONMENT SETUP ---
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

# --- 2. CONFIGURATION ---
GUI = False  # Set to True to watch the simulation
sumoBinary = "sumo-gui" if GUI else "sumo"

# Using relative paths for GitHub portability
CONFIG_PATH = os.path.join('environment', 'test.sumocfg')
Sumo_config = [sumoBinary, '-c', CONFIG_PATH, '--step-length', '0.1', '--delay', '0']

TOTAL_STEPS = 5000 
GAMMA = 0.95
EPSILON = 1.0
EPSILON_DECAY = 0.999
EPSILON_MIN = 0.01
BATCH_SIZE = 32
MEMORY_SIZE = 2000
MIN_GREEN_STEPS = 100

# --- 3. MODEL & AGENT ---
def build_model(state_size, action_size):
    model = keras.Sequential([
        layers.Input(shape=(state_size,)),
        layers.Dense(64, activation='relu'),
        layers.Dense(64, activation='relu'),
        layers.Dense(action_size, activation='linear')
    ])
    model.compile(loss='mse', optimizer=keras.optimizers.Adam(learning_rate=0.001))
    return model

# (Include your get_state, check_ambulance, apply_action functions here as in your original code)

# --- 4. MAIN TRAINING LOOP ---
if __name__ == "__main__":
    memory = deque(maxlen=MEMORY_SIZE)
    dqn_model = build_model(state_size=13, action_size=2)
    traci.start(Sumo_config)

    queue_history = []
    step = 0

    print("=== Starting Training ===")
    while step < TOTAL_STEPS:
        current_state = get_state()
        
        # Action Selection
        if np.random.rand() <= EPSILON:
            action = random.choice([0, 1])
        else:
            q_values = dqn_model.predict(current_state.reshape(1, -1), verbose=0)
            action = np.argmax(q_values[0])

        apply_action(action, step)
        traci.simulationStep()
        
        # Reward & History
        next_state = get_state()
        total_queue = np.sum(next_state[:-1])
        reward = -total_queue
        queue_history.append(total_queue)
        
        # Memory & Experience Replay
        memory.append((current_state, action, reward, next_state))
        if len(memory) > BATCH_SIZE:
            # (Insert your replay logic here)
            pass

        if EPSILON > EPSILON_MIN:
            EPSILON *= EPSILON_DECAY
        
        step += 1

    traci.close()
    
    # Save Results
    if not os.path.exists('results'): os.makedirs('results')
    if not os.path.exists('models'): os.makedirs('models')
    np.save("results/ai_queue_data.npy", queue_history)
    dqn_model.save("models/traffic_control_model.h5")
    print("Training Complete. Model and data saved.")
