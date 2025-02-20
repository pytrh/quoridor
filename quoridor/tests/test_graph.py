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

def test_a_star_simple():
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

def add_node():
    graph = Graph()
    node1 = (0,0)
    graph.add_node(node1)

def test_edge_exists(capsys):
    graph = Graph()
    node1 = (0,0)
    node2 = (0,1)
    with pytest.raises(NodeNotFoundError):
        graph.edge_exists(node1, node2)
        captured = capsys.readouterr()
        assert f"Node {node1} not found in graph" in captured.err

    graph.add_node(node1)
    with pytest.raises(NodeNotFoundError):
        graph.edge_exists(node1, node2)
        captured = capsys.readouterr()
        assert f"Node {node2} not found in graph" in captured.err

def test_add_edge(capsys):
    graph = Graph()
    node1 = (0,0)
    node2 = (0,1)
    with pytest.raises(NodeNotFoundError):
        graph.add_edge(node1, node2)
        captured = capsys.readouterr()
        assert f"Node {node1} not found in graph" in captured.err
    
    graph.add_node(node1)
    with pytest.raises(NodeNotFoundError):
        graph.add_edge(node1, node2)
        captured = capsys.readouterr()
        assert f"Node {node2} not found in graph" in captured.err
    
    graph.add_node(node2)
    graph.add_edge(node1, node2)
    assert True == graph.edge_exists(node1, node2)

def test_remove_edge(capsys):
    graph = Graph()
    node1 = (0,0)
    node2 = (0,1)

    with pytest.raises(NodeNotFoundError):
        graph.remove_edge(node1, node2)
        captured = capsys.readouterr()
        assert f"Node {node1} not found in graph" in captured.err

    graph.add_node(node1)
    with pytest.raises(NodeNotFoundError):
        graph.remove_edge(node1, node2)
        captured = capsys.readouterr()
        assert f"Node {node2} not found in graph" in captured.err

    graph.add_node(node2)
    graph.add_edge(node1, node2)
    assert True == graph.edge_exists(node1, node2)

    graph.remove_edge(node1, node2)
    assert False == graph.edge_exists(node1, node2)
    

def test_manhattan_distance(capsys):
    graph = Graph()
    node1 = (0,0)
    node2 = (0,1)

    with pytest.raises(NodeNotFoundError):
        graph.manhattan_distance(node1, node2)
        captured = capsys.readouterr()
        assert f"Node {node1} not found in graph" in captured.err

    graph.add_node(node1)
    with pytest.raises(NodeNotFoundError):
        graph.manhattan_distance(node1, node2)
        captured = capsys.readouterr()
        assert f"Node {node2} not found in graph" in captured.err
    
    graph.add_node(node2)
    assert 1 == graph.manhattan_distance(node1, node2)

    node3 = (0,-1)
    graph.add_node(node3)
    assert 1 == graph.manhattan_distance(node1, node3)

def test_a_star(capsys):
    graph = Graph()
    node1 = (0,0)
    node2 = (0,1)
    node3 = (0,-1)
    node4 = (0,-1)

    with pytest.raises(NodeNotFoundError):
        graph.a_star(node1, node2)
        captured = capsys.readouterr()
        assert f"Node {node1} not found in graph" in captured.err

    graph.add_node(node1)
    with pytest.raises(NodeNotFoundError):
        graph.a_star(node1, node2)
        captured = capsys.readouterr()
        assert f"Node {node2} not found in graph" in captured.err
    
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_node(node4)
    with pytest.raises(PathNotFoundError):
        graph.a_star(node1, node2)
        captured = capsys.readouterr()
        assert f"No path found between {node1} and {node2}" in captured.err
    
    graph.add_edge(node1, node2)
    graph.add_edge(node2, node3)
    
    assert [node1, node2] == graph.a_star(node1, node2)           
    assert [node1, node2, node3] == graph.a_star(node1, node3)

    graph.add_edge(node1, node4)
    graph.add_edge(node4, node2)
    assert not [node1, node4, node2] == graph.a_star(node1, node2)  

def test_breadth_first_search(capsys):
    graph = Graph()
    node1 = (0,0)
    node2 = (0,1)
    node3 = (0,-1)
    node4 = (0,-1)
    with pytest.raises(NodeNotFoundError):
        graph.breadth_first_search(node1, node2)
        captured = capsys.readouterr()
        assert f"Node {node1} not found in graph" in captured.err

    graph.add_node(node1)
    with pytest.raises(NodeNotFoundError):
        graph.breadth_first_search(node1, node2)
        captured = capsys.readouterr()
        assert f"Node {node2} not found in graph" in captured.err

    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_node(node4)
    with pytest.raises(PathNotFoundError):
        graph.breadth_first_search(node1, node2)
        captured = capsys.readouterr()
        assert f"No path found between {node1} and {node2}" in captured.err
    
    graph.add_edge(node1, node2)
    graph.add_edge(node2, node3)
    
    assert [node1, node2] == graph.breadth_first_search(node1, node2)           
    assert [node1, node2, node3] == graph.breadth_first_search(node1, node3)

    graph.add_edge(node1, node4)
    graph.add_edge(node4, node3)
    assert not graph.depth_first_search(node1, node2) == [node1, node4, node3, node2]

def test_depth_first_search(capsys):
    graph = Graph()
    node1 = (0,0)
    node2 = (0,1)
    node3 = (0,-1)
    node4 = (-1, 0)
    with pytest.raises(NodeNotFoundError):
        graph.depth_first_search(node1, node2)
        captured = capsys.readouterr()
        assert f"Node {node1} not found in graph" in captured.err

    graph.add_node(node1)
    with pytest.raises(NodeNotFoundError):
        graph.depth_first_search(node1, node2)
        captured = capsys.readouterr()
        assert f"Node {node2} not found in graph" in captured.err

    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_node(node4)
    with pytest.raises(PathNotFoundError):
        graph.depth_first_search(node1, node2)
        captured = capsys.readouterr()
        assert f"No path found between {node1} and {node2}" in captured.err
    
    graph.add_edge(node1, node2)
    graph.add_edge(node2, node3)
    
    assert [node1, node2] == graph.depth_first_search(node1, node2)           
    assert [node1, node2, node3] == graph.depth_first_search(node1, node3)

    graph.add_edge(node1, node4)
    graph.add_edge(node4, node3)
    assert graph.depth_first_search(node1, node2) == [node1, node4, node3, node2]  or  [node1, node2]

# test de limites
def test_limits():
    graph = Graph()
    i = 0
    stop = False
    while(not stop):
        i += 1
        graph.add_node((0, i - 1))
        if i > 1000000:
            stop = True
            
    i = 0
    stop = False
    while(not stop):
        i += 1
        graph.add_edge((0, i - 1), (0, i))
        assert graph.edge_exists((0, i - 1), (0, i))
        if i >= 1000000:
            stop = True

    assert 1000000 == graph.manhattan_distance((0,0), (0,i))
    assert [ (0, i) for i in range(1000001) ] == graph.a_star((0,0), (0,i))

if __name__ == "__main__":
    pytest.main()