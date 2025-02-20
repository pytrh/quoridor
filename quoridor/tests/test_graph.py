"""
Unit tests for the graph module
"""
import pytest
from src.graph import Graph
from src.exceptions import NodeNotFoundError, EdgeNotFoundError, PathNotFoundError

def test_graph():
    """
    Test the base functionality of the graph class
    """
    g = Graph()
    
    # Create a 2x2 grid graph
    size = 2
    for x in range(size):
        for y in range(size):
            g.add_node((x, y))
    
    # Add edges for a 2x2 grid
    edges = [((0, 0), (0, 1)), ((0, 0), (1, 0)), 
             ((0, 1), (1, 1)), ((1, 0), (1, 1))]
    for node1, node2 in edges:
        g.add_edge(node1, node2)
    
    # Check if nodes and edges are correctly added
    assert g.node_exists((0, 0))
    assert g.node_exists((1, 1))
    assert g.edge_exists((0, 0), (0, 1))
    assert g.edge_exists((1, 0), (1, 1))

    # # Check negative case for exists function 
    assert not g.node_exists((2,2))
    assert not g.node_exists((-1, -1))
    assert not g.edge_exists((1, 1), (1, 1))

    # # Check edges removal
    g.remove_edge((0, 0), (0, 1))
    assert not g.edge_exists((0, 0), (0, 1))
    assert not g.edge_exists((0, 1), (0, 0))

    # # Check negative case for edge removal
    with pytest.raises(EdgeNotFoundError):
        g.remove_edge((0, 0), (1, 1))
    with pytest.raises(EdgeNotFoundError):
        g.remove_edge((1, 1), (1, 1))

    # # Check nodes removal
    g.remove_node((1, 1))
    with pytest.raises(NodeNotFoundError):
        g.remove_node((1, 1))
    with pytest.raises(NodeNotFoundError):
        g.remove_node((2, 2))

def test_a_star():
    """
    Test the A* algorithm
    """
    graph = Graph()

    nodes = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for node in nodes:
        graph.add_node(node)
    
    edges = [((0, 0), (0, 1)),
             ((0, 1), (1, 1)),
             ((1, 1), (1, 0)),
             ((1, 0), (0, 0))]

    for node1, node2 in edges:
        graph.add_edge(node1, node2)
    
    start = (0, 0)
    goal = (1, 1)
    
    path = graph.a_star(start, goal)
    assert path == [(0, 0), (0, 1), (1, 1)] or path == [(0, 0), (1, 0), (1, 1)]
    assert len(path) == 3

    # Check negative case for A*
    graph.add_node((2, 2))
    with pytest.raises(PathNotFoundError):
        graph.a_star((0, 0), (2, 2))

if __name__ == "__main__":
    pytest.main()