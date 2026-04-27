from flask import Flask, jsonify, request
from flask_cors import CORS
import time
import random
import psutil
import os
import sys
import tempfile

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine_suboptimal.engine import DeliveryEngineSuboptimal
from engine_optimized.engine import DeliveryEngineOptimized
app = Flask(__name__)
CORS(app)

# Intentional system-pressure simulation state.
LEAK_BUFFER = []
FD_LEAKS = []

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024) # MB

@app.route('/api/benchmark', methods=['POST'])
def run_benchmark():
    data = request.json
    n_orders = data.get('n_orders', 1000)
    engine_type = data.get('engine_type', 'optimized')
    
    mem_before = get_memory_usage()
    start_time = time.time()
    
    results = {
        'steps': [],
        'total_time': 0,
        'memory_delta': 0
    }

    # Performance monitoring started

    # Memory and FD tracking
    
    if engine_type == 'suboptimal':
        engine = DeliveryEngineSuboptimal(city_nodes=100)
        # 1. Add Addresses
        s = time.time()
        for i in range(500): engine.add_address(f"Street {i}")
        results['steps'].append({'name': 'Load Addresses', 'time': time.time() - s})
        
        # 2. Add Orders
        s = time.time()
        for i in range(n_orders): engine.add_order(f"ORD-{i}", random.randint(1, 100))
        results['steps'].append({'name': 'Insert Orders', 'time': time.time() - s})
        
        # 3. Autocomplete
        s = time.time()
        for _ in range(50): engine.autocomplete("Street 1")
        results['steps'].append({'name': 'Autocomplete', 'time': time.time() - s})
        
        # 4. Route
        s = time.time()
        try:
            for i in range(20): engine.add_edge(i, i+1, 1)
            engine.find_route(0, 15)
        except Exception as e:
            print(f"Suboptimal route failed: {e}")
        results['steps'].append({'name': 'Route Discovery', 'time': time.time() - s})
        
    else:
        engine = DeliveryEngineOptimized()
        # 1. Add Addresses
        s = time.time()
        for i in range(500): engine.add_address(f"Street {i}")
        results['steps'].append({'name': 'Load Addresses', 'time': time.time() - s})
        
        # 2. Add Orders
        s = time.time()
        for i in range(n_orders): engine.add_order(f"ORD-{i}", random.randint(1, 100))
        results['steps'].append({'name': 'Insert Orders', 'time': time.time() - s})
        
        # 3. Autocomplete
        s = time.time()
        for _ in range(50): engine.autocomplete("Street 1")
        results['steps'].append({'name': 'Autocomplete', 'time': time.time() - s})
        
        # 4. Route
        s = time.time()
        for i in range(20): engine.add_edge(i, i+1, 1)
        engine.find_route(0, 15)
        results['steps'].append({'name': 'Route Discovery', 'time': time.time() - s})

    results['total_time'] = time.time() - start_time
    results['memory_delta'] = get_memory_usage() - mem_before
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
