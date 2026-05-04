# Depht first with iterative deepening 

path.pl :


The state space:

    s(a, b).
    s(a, c).
    s(b, d).
    s(b, e).
    s(d, h).
    s(e, i).
    s(e, j).
    s(c, f).
    s(c, g).
    s(f, k).

The Goal nodes:

    goal(j).
    goal(f).


    
  The path for a Node to itself its a list with that node.\
  This is the recursive stop condition.

    path(Node, Node, [Node]). % Single node path


   
We want to build a path from the FirstNode to the LastNode and the result will be a list with the LastNode as the Head, and the path.\
The list is reversed(end to begining)


    path(FirstNode, LastNode, [LastNode | Path]) :-
        path(FirstNode, OneButLast, Path), % Build the path until the OneButLastNode
        s(OneButLast, LastNode),           % Check wether there is a arc from the OneButLast to the last node
        \+ member(LastNode, Path).         % No cycle


    % ?- path(a, Last, Path).




depth-first-iterative-deepening:


    :- consult('path.pl').

    depth_first_iterative_deepening( Node, Solution) :-
        path( Node, GoalNode, Solution),
        goal( GoalNode).


    % ?- depth_first_iterative_deepening(a, Solution).


Portanto o que acontece aqui é que ele faz a pesquisa em profundidade primeiro, e portanto, ele gera todos os caminhos(path) desde o Node inicial até ao Goal node.
Contudo, para ser iterative deepening está incompleto, porque ele funciona com pesquisas por niveis.
