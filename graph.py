# contains functions for manipulating and performing operations on graphs,
# including shortest paths, reformatting, minimum spanning tree, etc. to
# allow more flexibility, many of the functions accept a function pointer
# that specifies how comparison between graph nodes should be performed;
# by default, the standard weighted edge format is assumed. i.e.
#
# adjacency list entry: at index u, (v, w); represents edge u~v, weight w
# edge list entry: (u, v, w); represents edge u~v, weight w
#
# Changelog:
#
# 05-23-2019
#
# initial creation. added bfs with option to return path or distances; can
# also work with boolean/int adjacency matrix as well.

# module name
_MODULE_NAME = "graph"

import math

def bfs(src, G, is_adjm = False, get_path = False):
    """
    standard breadth-first search algorithm. on an unweighted graph, it will
    return an array dist with |V(G)| entries, corresponding to the distances
    from the specified input node src to each other node in G (src is an int).

    the input graph G is treated as a directed graph with the adjacency list
    format if adj_M is False, else if adj_M is True, then G will be treated as
    an |V(G)| x |V(G)| adjacency matrix. the adjacency matrix can either be
    boolean or an int matrix; both True/Fals and > 0 will be tested.

    if get_path is True, then an array of integer lists will be returned that
    detail the paths from src to each other vertex in V(G).
    """
    # get length of G
    n = len(G)
    # return None if n < 1
    if n < 1: return None
    # initialize distance array
    dist = [math.inf for _ in range(n)]
    # intialize previous array
    prev = [None for _ in range(n)]
    # append src to a queue and set dist[src] to 0
    Q = [src]
    dist[src] = 0
    # while the queue is not empty
    while len(Q) > 0:
        # dequeue a node
        u = Q.pop(0)
        # if is_adjm is True, treat G as adjacency matrix
        if is_adjm == True:
            # update distances for all edges v in G[u], and enqueue v, as long
            # as the edges have not been visited before
            for v in range(n):
                if dist[v] == math.inf:
                    if (G[u][v] > 0) or (G[u][v] == True):
                        dist[v] = dist[u] + 1
                        Q.append(v)
                    # if get_path is True, set prev[v] to u
                    if get_path == True:
                        prev[v] = u
        # else treat as adjacency list
        else:
            # update distances for all edges in u's edge list, and enqueue, as
            # long as the edges have not been visited before
            for v in G[u]:
                if dist[v] == math.inf:
                    dist[v] = dist[u] + 1
                    Q.append(v)
                    # if get_path is True, set prev[v] to u
                    if get_path == True:
                        prev[v] = u
    # if get_path is True, create array of empty lists for each path from src to
    # each other node in the graph, and return the array
    if get_path == True:
        paths = [[] for i in range(n)]
        for v in range(n):
            # previous node
            pnode = v
            # while true
            while pnode is not None:
                # prepend previous node number and set pnode to its prev
                paths[v].insert(0, pnode)
                pnode = prev[pnode]
        # return paths
        return paths
    # else just return dist
    return dist

if __name__ == "__main__":
    print("{0}: do not run as standalone module".format(_MODULE_NAME))
