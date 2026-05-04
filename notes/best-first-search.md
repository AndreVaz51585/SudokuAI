# best first search - A* (informed alghorithm)


Its called an informed alghorithm because it has more information beyhond the nodes, on this case we have the heuristic.
So we search based on the heuristic, and this is the heuristic predicate:

    succlist( _, [], []).

    succlist( GO, [N/C | NCs], Ts) :-
        G is GO + C,
        h( N, H),     % Heuristic term h(N)
        F is G + H,
        succlist( GO, NCs, Ts1),
        insert( l(N, F/G), Ts1, Ts).

-  G is GO + C, its the accumulated cost from the initial node until the node N.

- h( N, H), estimated cost until the goal node

- F is G + H, value used to sort the nodes


So we always choose the node with the lowest \

**f(n) = g(n) + h(n)**

**g(n)** - the acumulated cost

**h(n)** - estimated cost until the goal node

