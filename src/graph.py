#!/usr/bin/python
# -*- coding: utf-8 -*-


class Graph(object):

    def __init__(self, *args, **kwargs):
        self.node_neighbors = {}
        self.visited = {}

    def add_nodes(self, nodelist):
        for node in nodelist:
            self.add_node(node)

    def add_node(self, node):
        if not node in self.nodes():
            self.node_neighbors[node] = []

    def add_edge(self, edge):
        u, v = edge
        if(v not in self.node_neighbors[u]) and (u not in self.node_neighbors[v]):
            self.node_neighbors[u].append(v)

            if(u != v):
                self.node_neighbors[v].append(u)

    def add_edges(self, edgelist):
        for edge in edgelist:
            self.add_edge(edge)

    def nodes(self):
        return self.node_neighbors.keys()

    def edges(self):
        return self.node_neighbors.items()

    def __len__(self):
        return len(self.node_neighbors)

    def __repr__(self):
        lst = [ "%s: %s" % (k, v) for k, v in self.node_neighbors.items()]
        lst.insert(0, '{')
        lst.append('}')
        return "\n ".join(lst)

    def depth_first_search(self, root=None):
        order = []
        self.visited.clear()

        def dfs(node):
            self.visited[node] = True
            order.append(node)
            for n in self.node_neighbors[node]:
                if not n in self.visited:
                    dfs(n)

        if root:
            dfs(root)

        for node in self.nodes():
            if not node in self.visited:
                dfs(node)

        # print order
        return order

    def breadth_first_search(self, root=None):
        queue = []
        order = []
        self.visited.clear()

        def bfs():
            while len(queue) > 0:
                node = queue.pop(0)

                self.visited[node] = True
                for n in self.node_neighbors[node]:
                    if (not n in self.visited) and (not n in queue):
                        queue.append(n)
                        order.append(n)

        if root:
            queue.append(root)
            order.append(root)
            bfs()

        for node in self.nodes():
            if not node in self.visited:
                queue.append(node)
                order.append(node)
                bfs()

        # print order
        return order

# --------------
#  search path
# --------------


def find_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if not start in graph:
        return None
    for node in graph[start]:
        if node not in path:
            newpath = find_path(graph, node, end, path)
            if newpath:
                return newpath
    return None


def find_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if not start in graph:
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths


def find_shortest_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if not start in graph:
        return None
    shortest = None
    for node in graph[start]:
        if node not in path:
            newpath = find_shortest_path(graph, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest


"""
    1
    ---
   /   \
  2     3
 / \    /\
4   5  6  7
 \ /
  8
"""

if __name__ == '__main__':
    g = Graph()
    g.add_nodes([i + 1 for i in range(8)])
    g.add_edge((1, 2))
    g.add_edge((1, 3))
    g.add_edge((2, 4))
    g.add_edge((2, 5))
    g.add_edge((4, 8))
    g.add_edge((5, 8))
    g.add_edge((3, 6))
    g.add_edge((3, 7))
    g.add_edge((6, 7))
    print "graph:", g
    print "nodes:", g.nodes()
    print "edges:", g.edges()

    bfs_order = g.breadth_first_search(1)
    dfs_order = g.depth_first_search(1)
    print "bfs:", bfs_order
    print "dfs:", dfs_order

    graph = dict(g.edges())
    start, end = 1, 8
    print 'path:', find_path(graph, start, end)
    print 'all_path:', find_all_paths(graph, start, end)
    print 'shortest_path:', find_shortest_path(graph, start, end)
