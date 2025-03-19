from agent.components.text2cypher.validation.utils.regex_patterns import (
    get_node_label_pattern,
)


def test_get_node_label_pattern() -> None:
    pat = get_node_label_pattern()
    assert pat.findall("(n:Node)")[0] == "Node"
    assert pat.findall("(m {id:'001'})") == []
    assert pat.findall("(nodeA:Node {id:'001'})")[0] == "Node "
    assert pat.findall("(node_1:N)")[0] == "N"
    assert pat.findall("(node_1:Node{id:'001'})")[0] == "Node"
    assert pat.findall("(nodeA:`Node one` {id:'001'})")[0] == "Node one"
    assert pat.findall("(node_1:Node|NodeB{id:'001'})")[0] == "Node|NodeB"
    assert pat.findall("(node_1:Node&NodeB {id:'001'})")[0] == "Node&NodeB "
