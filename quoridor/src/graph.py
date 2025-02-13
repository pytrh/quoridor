"""graph module to represent the game board"""

class Graph:
    def __init__(self):
        self._graph = {}

    def add_node(self, node):
        if node not in self._graph:
            self._graph[node] = set()

    def add_edge(self, node1, node2):
        self.add_node(node1)
        self.add_node(node2)
        self._graph[node1].add(node2)
        self._graph[node2].add(node1) 

    def edge_exists(self, node1, node2):
        return node1 in self._graph and node2 in self._graph[node1]
    
    def node_exists(self, node):
        return node in self._graph
    
    def remove_node(self, node):
        if node in self._graph:
            for v in self._graph[node]:
                self._graph[v].remove(node)
            del self._graph[node]
        else:
            raise ValueError(f"Node {node} not found in graph")

    def remove_edge(self, node1, node2):
        if node1 in self._graph and node2 in self._graph:
            self._graph[node1].remove(node2)
            self._graph[node2].remove(node1)

    """
    Breadth-First Search to find the shortest path between two nodes
    """
    def BFS(self, node1, node2):
        if node1 not in self._graph or node2 not in self._graph:
            return None

        visited = set()
        queue = [[node1]]
        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node == node2:
                return path
            if node not in visited:
                for adjacent in self._graph[node]:
                    new_path = list(path)
                    new_path.append(adjacent)
                    queue.append(new_path)
                visited.add(node)
        return None
    
    """
    Depth-First Search to find if there is a path between two nodes
    """
    def DFS(self, node1, node2):
        if node1 not in self._graph or node2 not in self._graph:
            return None

        visited = set()
        stack = [node1]
        while stack:
            node = stack.pop()
            if node == node2:
                return True
            if node not in visited:
                for adjacent in self._graph[node]:
                    stack.append(adjacent)
                visited.add(node)
        return False

# Do we need the following methods?
    def __str__(self):
        return str(self._graph)

    def get_nodes(self):
        return list(self._graph.keys())

    def get_edges(self, node):
        return list(self._graph[node])
