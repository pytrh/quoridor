"""
Limits tests for the graph module
"""

import random
import pytest
from quoridor.graph import Graph


def add_nodes_to_graph(graph, size):
    """
    Adds nodes to the graph in a grid pattern of size `size` x `size`.
    """
    for row in range(size):
        for col in range(size):
            graph.add_node((row, col))


def add_edges_to_graph(graph, size):
    """
    Adds edges between adjacent nodes in the grid.
    """
    for row in range(size):
        for col in range(size):
            if row + 1 < size:
                graph.add_edge((row, col), (row + 1, col))
                assert graph.edge_exists((row, col), (row + 1, col))
            if col + 1 < size:
                graph.add_edge((row, col), (row, col + 1))
                assert graph.edge_exists((row, col), (row, col + 1))


def remove_random_edges(graph, size):
    """
    Removes random edges between adjacent nodes in the grid.
    """
    for row in range(size):
        for col in range(size):
            if row + 1 < size:
                if random.random() < 0.1:
                    graph.remove_edge((row, col), (row + 1, col))
                    assert not graph.edge_exists((row, col), (row + 1, col))
            if col + 1 < size:
                if random.random() < 0.1:
                    graph.remove_edge((row, col), (row, col + 1))
                    assert not graph.edge_exists((row, col), (row, col + 1))


@pytest.mark.limit
def test_limits():
    """
    Test the limits of the graph's methods.
    """
    graph = Graph()

    size = 1000
    add_nodes_to_graph(graph, size)
    print("Creating 1 000 000 nodes")

    add_edges_to_graph(graph, size)
    print("\nConnecting all nodes")

    print("[x] - [x] - [x] -  . . . - [x]")
    print(" |     |     |     . . .    |")
    print("[x] - [x] - [x] -  . . . - [x]")
    print(" |     |     |     . . .    |")
    print("[x] - [x] - [x] -  . . . - [x]")
    print(" .     .     .     . . .    .")
    print(" .     .     .     . . .    .")
    print(" .     .     .     . . .    .")
    print("[x] - [x] - [x] -  . . . - [x]")

    remove_random_edges(graph, size)
    print("\nRemoving random edges")

    print("[x] - [x] - [x] -  . . . - [x]")
    print(" |                 . . .    |")
    print("[x] - [x]   [x] -  . . . - [x]")
    print("       |     |     . . .     ")
    print("[x]   [x] - [x] -  . . . - [x]")
    print(" .     .     .     . . .    .")
    print(" .     .     .     . . .    .")
    print(" .     .     .     . . .    .")
    print("[x] - [x]   [x] -  . . . - [x]")

    start = (0, 0)
    end = (size - 1, size - 1)
    path = graph.a_star(start, end)
    assert path is not None
    assert path[0] == start
    assert path[-1] == end
    assert len(path) >= 1

    print("\nFinding a path with a_star")
    print("[x]===[x]===[x]==+ . . . +=[x]")
    print(" |                 . . .    |")
    print("[x]===[x]   [x] -  . . . - [x]")
    print("       +           . . .     ")
    print("[x] - [x]===[x] -  . . . - [x]")
    print(" .     .     +     . . .    .")
    print(" .     .  +  .     . . .    .")
    print(" .     +     .     . . .    .")
    print("[x]===[x] - [x] -  . . . - [x]")

    print("\nLength a_star array")
    print(len(path))

    manhattan_dist = graph.manhattan_distance(start, end)
    assert manhattan_dist == (size - 1) * 2
    print("\nManhattan distance")
    print(manhattan_dist)
