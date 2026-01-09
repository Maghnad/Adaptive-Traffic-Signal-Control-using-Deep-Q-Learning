import traci
import numpy as np
from tensorflow import keras
import os

# Set Epsilon to 0 for pure exploitation (no random moves)
EPSILON = 0.0 
MODEL_PATH = "models/traffic_control_model.h5"

if os.path.exists(MODEL_PATH):
    model = keras.models.load_model(MODEL_PATH)
    print("Loaded trained model for testing.")
else:
    print("No model found. Please run main.py first.")
    exit()

# Start traci in GUI mode to demonstrate
traci.start(["sumo-gui", "-c", "environment/test.sumocfg"])

for step in range(2000):
    state = get_state() # Use the same function as main.py
    q_values = model.predict(state.reshape(1, -1), verbose=0)
    action = np.argmax(q_values[0])
    
    apply_action(action, step)
    traci.simulationStep()

traci.close()
