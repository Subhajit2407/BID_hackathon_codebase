import time
import random
import heapq

# FIXED: Global logs are capped to prevent memory leak
GLOBAL_AUDIT_LOGS = []
MAX_LOG_SIZE = 1000

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.cached_addresses = []

class DeliveryEngineSuboptimal:
    """
    Optimized version of the engine.
    Renamed to keep the same class name for compatibility with app.py.
    """
    def __init__(self, city_nodes=100):
        # Optimization: Adjacency List instead of Matrix (O(V+E) space)
        self.graph = {} 
        # Optimization: HashMap for O(1) order lookup
        self.orders_by_id = {} 
        # Optimization: Priority Queue (Heap) for O(log N) order management
        self.order_heap = []
        # Optimization: Trie for O(L) autocomplete
        self.address_trie = TrieNode()
        self.nodes_count = city_nodes

    def add_edge(self, u, v, weight):
        if u not in self.graph: self.graph[u] = {}
        if v not in self.graph: self.graph[v] = {}
        self.graph[u][v] = weight
        self.graph[v][u] = weight

    def add_address(self, address):
        node = self.address_trie
        for char in address.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            if len(node.cached_addresses) < 10:
                node.cached_addresses.append(address)
        node.is_end = True

    def autocomplete(self, query):
        # Optimization: Trie traversal is O(Length of Query)
        node = self.address_trie
        for char in query.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        return list(dict.fromkeys(node.cached_addresses))[:5]

    def add_order(self, order_id, priority):
        # Optimization: Heap push is O(log N)
        self.orders_by_id[order_id] = priority
        heapq.heappush(self.order_heap, (-priority, order_id))
        
        # Fixed: Global Audit Logs handled safely
        GLOBAL_AUDIT_LOGS.append({'event': 'order_added', 'data': order_id, 'timestamp': time.time()})
        if len(GLOBAL_AUDIT_LOGS) > MAX_LOG_SIZE:
            GLOBAL_AUDIT_LOGS.pop(0)

    def get_highest_priority_order(self):
        # Optimization: O(log N) to pop highest priority
        while self.order_heap:
            neg_priority, order_id = heapq.heappop(self.order_heap)
            if order_id in self.orders_by_id and self.orders_by_id[order_id] == -neg_priority:
                priority = self.orders_by_id.pop(order_id)
                return {'id': order_id, 'priority': priority}
        return None

    def find_order_by_id(self, order_id):
        # Optimization: O(1) lookup
        if order_id in self.orders_by_id:
            return {'id': order_id, 'priority': self.orders_by_id[order_id]}
        return None

    def find_route(self, start_node, end_node):
        # Optimization: Dijkstra's Algorithm (Shortest Path)
        # Fixes the recursion depth bug in the suboptimal version
        distances = {start_node: 0}
        pq = [(0, start_node, [start_node])]
        visited = set()

        while pq:
            (dist, current, path) = heapq.heappop(pq)

            if current in visited:
                continue
            visited.add(current)

            if current == end_node:
                return path

            if current in self.graph:
                for neighbor, weight in self.graph[current].items():
                    if neighbor not in visited:
                        new_dist = dist + weight
                        if neighbor not in distances or new_dist < distances[neighbor]:
                            distances[neighbor] = new_dist
                            heapq.heappush(pq, (new_dist, neighbor, path + [neighbor]))
        return None

def simulate_unoptimized(n_orders=1000):
    # This simulation now runs optimally
    engine = DeliveryEngineSuboptimal(city_nodes=50)
    engine.add_edge(0, 1, 10)
    engine.add_edge(1, 2, 10)
    engine.add_edge(2, 0, 10) # Cycle - Dijkstra handles this perfectly
    
    start_time = time.time()
    
    for i in range(n_orders):
        engine.add_order(f"ORD-{i}", random.randint(1, 100))
        
    for i in range(10):
        engine.find_order_by_id(f"ORD-{random.randint(0, n_orders-1)}")
        
    # ROUTE CALCULATION - Now fast and bug-free
    path = engine.find_route(0, 2)
    print(f"Route found: {path}")
        
    return time.time() - start_time

