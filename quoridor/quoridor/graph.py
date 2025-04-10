"""
Graph module.
"""

import heapq
from typing import Callable
from quoridor.exceptions import NodeNotFoundError, EdgeNotFoundError, PathNotFoundError


class Graph:
    """
    Graph class to represent the game board.
    """

    def __init__(self) -> None:
        """
        Initialize a new graph, a dictionary of nodes and their adjacent nodes.
        """
        self._graph = {}

    def add_node(self, node: tuple[int, int]) -> None:
        """
        Add a node to the graph, if it is not already in the graph by
        adding a integer tuple as a key to the dictionary.

        :param node: The node to add to the graph.
        :type node: tuple[int, int]
        """
        if node not in self._graph:
            self._graph[node] = set()

    def add_edge(self, node1: tuple[int, int], node2: tuple[int, int]) -> None:
        """
        Add an edge between two nodes by adding them to each other's adjacency list.

        :param node1: The first node.
        :type node1: tuple[int, int]
        :param node2: The second node.
        :type node2: tuple[int, int]
        :raises NodeNotFoundError: If either node is not found in the graph.
        """
        if node1 not in self._graph:
            raise NodeNotFoundError(f"Node {node1} not found in graph")
        if node2 not in self._graph:
            raise NodeNotFoundError(f"Node {node2} not found in graph")
        self._graph[node1].add(node2)
        self._graph[node2].add(node1)

    def edge_exists(self, node1: tuple[int, int], node2: tuple[int, int]) -> bool:
        """
        Check if an edge exists between two nodes.

        :param node1: The first node.
        :type node1: tuple[int, int]
        :param node2: The second node.
        :type node2: tuple[int, int]
        :raises NodeNotFoundError: If either node is not found in the graph.
        """
        if node1 not in self._graph:
            raise NodeNotFoundError(f"Node {node1} not found in graph")
        if node2 not in self._graph:
            raise NodeNotFoundError(f"Node {node2} not found in graph")
        return node2 in self._graph[node1]

    def node_exists(self, node: tuple[int, int]) -> bool:
        """
        Check if a node exists in the graph.

        :param node: The node to check.
        :type node: tuple[int, int]
        :return: True if the node exists in the graph, False otherwise.
        :rtype: bool
        """
        return node in self._graph

    def remove_node(self, node: tuple[int, int]) -> None:
        """
        Remove a node from the graph.

        :param node: The node to remove.
        :type node: tuple[int, int]
        :raises NodeNotFoundError: If the node is not found in the graph.
        """
        if node in self._graph:
            for connect_node in self._graph[node]:
                self._graph[connect_node].remove(node)
            del self._graph[node]
        else:
            raise NodeNotFoundError(f"Node {node} not found in graph")

    def remove_edge(self, node1: tuple[int, int], node2: tuple[int, int]) -> None:
        """
        Remove an edge between two nodes.

        :param node1: The first node.
        :type node1: tuple[int, int]
        :param node2: The second node.
        :type node2: tuple[int, int]
        :raises NodeNotFoundError: If either node is not found in the graph.
        """
        if node1 not in self._graph:
            raise NodeNotFoundError(f"Node {node1} not found in graph")
        if node2 not in self._graph:
            raise NodeNotFoundError(f"Node {node2} not found in graph")
        if node2 not in self._graph[node1]:
            raise EdgeNotFoundError(f"Edge {node1} -> {node2} not found in graph")
        self._graph[node1].remove(node2)
        self._graph[node2].remove(node1)

    def manhattan_distance(self, node1: tuple[int, int], node2: tuple[int, int]) -> int:
        """
        Calculate the Manhattan distance between two nodes.

        :param node1: The first node.
        :type node1: tuple[int, int]
        :param node2: The second node.
        :type node2: tuple[int, int]
        :raises NodeNotFoundError: If either node is not found in the graph.
        """
        if node1 not in self._graph:
            raise NodeNotFoundError(f"Node {node1} not found in graph")
        if node2 not in self._graph:
            raise NodeNotFoundError(f"Node {node2} not found in graph")
        return abs(node1[0] - node2[0]) + abs(node1[1] - node2[1])

    def a_star(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """
        A* Search to find the shortest path between two nodes.

        :param start: The starting node.
        :type start: tuple[int, int]
        :param goal: The goal node.
        :type goal: tuple[int, int]
        :raises NodeNotFoundError: If either node is not found in the graph.
        :raises PathNotFoundError: No path exist between the two nodes
        """
        if start not in self._graph:
            raise NodeNotFoundError(f"Node {start} not found in graph")
        if goal not in self._graph:
            raise NodeNotFoundError(f"Node {goal} not found in graph")

        visited = set()
        previous = {}
        costs = {}
        costs[start] = 0
        priority_queue = []
        heapq.heappush(priority_queue, (0, start))
        while priority_queue:
            score, node = heapq.heappop(priority_queue)
            if node == goal:
                reverse_path = []
                while node != start:
                    reverse_path.append(node)
                    node = previous[node]
                reverse_path.append(start)
                return reverse_path[::-1]
            if node not in visited:
                for adjacent in self._graph[node]:
                    new_cost = costs[node] + 1
                    if adjacent not in visited:
                        previous[adjacent] = node
                        costs[adjacent] = new_cost
                        heapq.heappush(
                            priority_queue,
                            (score + self.manhattan_distance(adjacent, goal), adjacent),
                        )
                visited.add(node)
        raise PathNotFoundError(f"No path found between {start} and {goal}")

    def a_star_modified(
        self, start: tuple[int, int], distance_to_goal: Callable[[tuple[int, int]], int]
    ) -> list[tuple[int, int]]:
        """
        A* Search to find the shortest path from a node to any nodes 
        that satisfies the distance_to_goal function.
        For example, if the distance_to_goal function is the manhattan distance to W, 
        the function will find the shortest path to any node in W.

        :param start: The starting node.
        :type start: tuple[int, int]
        :param distance_to_goal: The distance to the goal node.
        :type distance_to_goal: Callable[[tuple[int, int]], int]
        :raises NodeNotFoundError: If either node is not found in the graph.
        :raises PathNotFoundError: No path exist between the two nodes
        """
        if start not in self._graph:
            raise NodeNotFoundError(f"Node {start} not found in graph")

        visited = set()
        previous = {}
        costs = {}
        costs[start] = 0
        priority_queue = []
        heapq.heappush(priority_queue, (0, start))
        while priority_queue:
            score, node = heapq.heappop(priority_queue)
            if distance_to_goal(node) == 0:
                reverse_path = []
                while node != start:
                    reverse_path.append(node)
                    node = previous[node]
                reverse_path.append(start)
                return reverse_path[::-1]
            if node not in visited:
                for adjacent in self._graph[node]:
                    new_cost = costs[node] + 1
                    if adjacent not in visited:
                        previous[adjacent] = node
                        costs[adjacent] = new_cost
                        heapq.heappush(
                            priority_queue,
                            (score + distance_to_goal(adjacent), adjacent),
                        )
                visited.add(node)
        raise PathNotFoundError(f"No path found between {start} and goals.")

    def breadth_first_search(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """
        Breadth-First Search to find the shortest path between two nodes.

        :param start: The starting node.
        :type start: tuple[int, int]
        :param goal: The goal node.
        :type goal: tuple[int, int]
        :raises NodeNotFoundError: If either node is not found in the graph.
        """
        if start not in self._graph:
            raise NodeNotFoundError(f"Node {start} not found in graph")
        if goal not in self._graph:
            raise NodeNotFoundError(f"Node {goal} not found in graph")

        queue = [[start]]
        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node == goal:
                return path
            for adjacent in self._graph[node]:
                new_path = list(path)
                new_path.append(adjacent)
                queue.append(new_path)
        raise PathNotFoundError(f"No path found between {start} and {goal}")

    def depth_first_search(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """
        Depth-First Search to find a pseudo-random path between two nodes.

        :param start: The starting node.
        :type start: tuple[int, int]
        :param goal: The goal node.
        :type goal: tuple[int, int]
        :raises NodeNotFoundError: If either node is not found in the graph.
        """
        if start not in self._graph:
            raise NodeNotFoundError(f"Node {start} not found in graph")
        if goal not in self._graph:
            raise NodeNotFoundError(f"Node {goal} not found in graph")

        visited = set()
        stack = [[start]]
        while stack:
            path = stack.pop()
            node = path[-1]
            if node == goal:
                return path
            if node not in visited:
                for adjacent in self._graph[node]:
                    new_path = list(path)
                    new_path.append(adjacent)
                    stack.append(new_path)
                visited.add(node)
        raise PathNotFoundError(f"No path found between {start} and {goal}")
