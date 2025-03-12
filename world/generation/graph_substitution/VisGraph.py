from world.generation.graph_substitution.Graph import *
import graphviz

def view_graph(x:Graph, data_title=None):
    dot = graphviz.Digraph(comment='Graph')
    for node in x.nodes:
        if data_title is not None:
            dot.node(node.id, "{}\n{}".format(node.id, node.data[data_title]))
        else:
            dot.node(node.id, node.id)
    for edge in x.edges:
        dot.edge(edge.tail, edge.head)
    print(dot.source)  # doctest: +NORMALIZE_WHITESPACE
    dot.render('test-output/view_graph.gv', view=True)  # doctest: +SKIP

def view_graph_grid(x:Graph, loc_title,data_title=None):
    dot = graphviz.Digraph(comment='Graph', engine='neato')
    for node in x.nodes:
        pos_str = "{},{}!".format(node.data[loc_title][0],node.data[loc_title][1])
        if data_title is not None:
            dot.node(node.id, "{}\n{}".format(node.id, node.data[data_title]),pos=pos_str)
        else:
            dot.node(node.id, node.id,pos=pos_str)
    for edge in x.edges:
        dot.edge(edge.tail, edge.head)
    print(dot.source)  # doctest: +NORMALIZE_WHITESPACE
    dot.render('test-output/view_graph_grid.gv', view=True)  # doctest: +SKIP

