"""Unit tests for the graph module"""
import pytest
from src.graph import Graph

def test_graph():
    """Test the graph function"""
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

    # Check negative case for exists function 
    assert not g.node_exists((2,2))
    assert not g.node_exists((-1, -1))
    assert not g.edge_exists((1, 1), (1, 1))

    # Check edges removal
    g.remove_edge((0, 0), (0, 1))
    assert not g.edge_exists((0, 0), (0, 1))
    assert not g.edge_exists((0, 1), (0, 0))

    # Check nodes removal
    g.remove_node((1, 1))
    assert not g.node_exists((1, 1))
    assert not g.edge_exists((0, 0), (1, 1))
    assert not g.edge_exists((0, 1), (1, 1))
    assert not g.edge_exists((1, 0), (1, 1))

if __name__ == "__main__":
    pytest.main()