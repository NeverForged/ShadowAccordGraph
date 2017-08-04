import sys
import networkx as nx
import nxpd as nxpd
import matplotlib.pyplot as plt
import matplotlib.font_manager
from collections import Counter

def main():
    '''
    Loads the character edges file.
    '''
    G = nx.read_edgelist('data/character_edges.csv', delimiter=',')
    # print len(G.nodes())
    for node in G.degree():
        if G.degree(node) <= 1:
            G.remove_node(node)
    return G


def six_degress():
    '''
    Uses the various edges provided in the file to determine the seperation
    between two characters.  Also provides a 'Wick Number' for each.
    '''
    G = main()
    char1 = sys.argv[1]
    char2 = sys.argv[2]
    lst = nx.shortest_path(G, char1, char2)
    ret = ''
    n = len(lst)-1
    betweenness_centrality = nx.betweenness_centrality(G)
    #print Counter(betweenness_centrality).most_common(10)
    bacon = Counter(betweenness_centrality).most_common(1)[0][0]
    print 'Distance: {}'.format(len(lst))
    ret = ''
    for i, char in enumerate(lst):
        if i == n:
            bacon_num = len(nx.shortest_path(G, char, bacon))-1
            ret = ret + '{} ({} Number: {})'.format(char, bacon, bacon_num)
        else:
            bacon_num = len(nx.shortest_path(G, char, bacon))-1
            ret = ret + '{} ({} Number: {})'.format(char, bacon, bacon_num)
            ret = ret + "\n" + "   -knows...\n"
    print ret


def make_graph():
    '''
    '''
    G = main()

    # print len(G.nodes())
    set_pos = nx.spring_layout(G)
    # set_pos = nx.shell_layout(G)
    # set_pos = nx.fruchterman_reingold_layout(G, iterations=100)
    # set_pos = nx.spectral_layout(G, dim=2, weight='weight', scale=1.0, center=None)


    # Color subgroups...
    print "finding communities..."
    lst_com = find_communities_modularity(G)
    print "                   ...{} communities found".format(len(lst_com))
    # lst_com = find_communities_n(G, 5)
    lst_colors = ['b', 'r', 'g', 'c', 'm', 'k', 'y']
    # node_color = sequence of colors with the same length as nodelist.
    nodelist_color = G.nodes()
    for i, lst in enumerate(lst_com):
        for node in lst:
            nodelist_color[nodelist_color.index(node)] = lst_colors[i]
    # print nodelist_color
    nx.draw_networkx(G,
                     pos=set_pos,
                     arrows=False,
                     with_labels=False,
                     node_color=nodelist_color,
                     node_size=400,
                     alpha=0.33)
    nx.draw_networkx_labels(G,
                            pos=set_pos,
                            font_family='fantasy',
                            font_weight='bold')
    # nx.draw_graphviz(G)
    # plt.legend()

    degree_centrality = nx.degree_centrality(G)
    print "Degree Centrality (Most Connections)\n"
    for name in Counter(degree_centrality).most_common(10):
        print '    {}\n'.format(name)
    betweenness_centrality = nx.betweenness_centrality(G)
    print "Betweenness Centrality (Most Connections Made Thru)\n"
    for name in Counter(betweenness_centrality).most_common(10):
        print '    {}\n'.format(name)
    eigenvector_centrality = nx.eigenvector_centrality(G)
    print "Eigenvector Centrality (Err... most behind the scenes connected?)\n"
    for name in Counter(eigenvector_centrality).most_common(10):
        print '    {}\n'.format(name)

    # keep this last
    plt.show()


def girvan_newman_step(G):
    """Run one step of the Girvan-Newman community detection algorithm.

    Afterwards, the graph will have one more connected component.

    Parameters

    function GirvanNewman:
    repeat:
        repeat until a new connected component is created:
            calculate the edge betweenness centralities for all the edges
            remove the edge with the highest betweenness
    ----------
    G: networkx Graph object

    Returns
    -------
    None
    """
    n_coms = nx.number_connected_components(G)
    n_init = n_coms
    while n_init == n_coms:
        ebc = nx.edge_betweenness_centrality(G)
        G.remove_edge(*max(ebc, key=ebc.get))
        n_coms = nx.number_connected_components(G)


def find_communities_n(G, n):
    """Return communites of G after running Girvan-Newman algorithm n steps.

    Parameters
    ----------
    G: networkx Graph object
    n: int

    Returns
    -------
    list of lists
    """
    G1 = G.copy()
    for i in xrange(n):
        girvan_newman_step(G1)
    return list(nx.connected_components(G1))


def find_communities_modularity(G, max_iter=None):
    """Return communities with the maximum modulairty from G.

    Run Girvan-Newman algorithm on G and find communities with max modularity.

    Parameters
    ----------
    G: networkx Graph object
    max_iter: int, (optional, default=None)
        Maximum number of iterations

    Returns
    -------
    list of lists of strings
        Strings are node names
    """
    degrees = G.degree()
    num_edges = G.number_of_edges()
    G1 = G.copy()
    best_modularity = -1.0
    best_comps = nx.connected_components(G1)
    i = 0
    while G1.number_of_edges() > 0:
        subgraphs = nx.connected_component_subgraphs(G1)
        modularity = get_modularity(subgraphs, degrees, num_edges)
        if modularity > best_modularity:
            best_modularity = modularity
            best_comps = list(nx.connected_components(G1))
        girvan_newman_step(G1)
        i += 1
        if max_iter and i >= max_iter:
            break
    return best_comps


def get_modularity(subgraphs, degrees, num_edges):
    """Return the value of the modularity for the graph G.

    Parameters
    ----------
    subgraphs: generator
        Graph broken in subgraphs
    degrees: dictionary
        Node: degree key-value pairs from original graph
    num_edges: float
        Number of edges in original graph

    Returns
    -------
    float
        Modularity value, between -0.5 and 1
    """
    for subgraph in subgraphs:
        nodes = nx.nodes(subgraph)
        edges = nx.edges(subgraph)
        m = num_edges
        modularity = 0
        for i in nodes:
            for j in nodes:
                #if i != j:
                a = 0
                if (i, j) in edges:
                    a = 1
                modularity = modularity + a - degrees[i]*degrees[j]/float(2*m)
    return (1/float(2*m))*modularity

if __name__ == '__main__':
    if len(sys.argv) > 1:
        six_degress()
    else:
        make_graph()
