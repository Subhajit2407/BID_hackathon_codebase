import time
import heapq

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.addresses = [] # Store full addresses at this node

class DeliveryEngineOptimized:
    def __init__(self):
        self.graph = {} # Adjacency List: {node: {neighbor: weight}}
        self.orders_by_id = {} # {order_id: priority}
        self.order_heap = [] # Priority Queue: [(-priority, order_id)]
        self.address_trie = TrieNode()
        self.address_count = 0

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
            if len(node.addresses) < 10: # Limit cached results for memory
                node.addresses.append(address)
        node.is_end = True
        self.address_count += 1

    def autocomplete(self, query):
        node = self.address_trie
        for char in query.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Return unique addresses found at this prefix
        return list(dict.fromkeys(node.addresses))[:5]

    def add_order(self, order_id, priority):
        self.orders_by_id[order_id] = priority
        heapq.heappush(self.order_heap, (-priority, order_id))

    def get_highest_priority_order(self):
        while self.order_heap:
            neg_priority, order_id = heapq.heappop(self.order_heap)
            # Check if it was updated or removed (though not implemented here)
            if order_id in self.orders_by_id and self.orders_by_id[order_id] == -neg_priority:
                priority = self.orders_by_id.pop(order_id)
                return {'id': order_id, 'priority': priority}
        return None

    def find_order_by_id(self, order_id):
        if order_id in self.orders_by_id:
            return {'id': order_id, 'priority': self.orders_by_id[order_id]}
        return None

    def find_route(self, start_node, end_node):
        # Dijkstra's Algorithm
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
