# file for testing the different functions in pyalgos

import graph

if __name__ == "__main__":
    src = 0
    G = [[1, 2, 4], [], [3, 4, 5], [], [3, 5], []]
    print("graph.bfs({0}, {1},\n          get_path = True) ->\n{2}".format(
        src, G, graph.bfs(src, G, get_path = True)))
    G = [[False, True, True, False, True, False],
         [False, False, False, False, False, False],
         [False, False, False, True, True, True],
         [False, False, False, False, False, False],
         [False, False, False, True, False, True],
         [False, False, False, False, False, False]]
    print("graph.bfs({0}, {1},\n          is_adjm = True, get_path = True,) ->"
          "\n{2}".format(src, G, graph.bfs(src, G, is_adjm = True,
                                           get_path = True)))
