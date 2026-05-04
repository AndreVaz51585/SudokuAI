:- module(a_star, [bestfirst/2]).

:- use_module('../logic/operators').

% ==============================================
% LIGAÇÃO AO SUDOKU
% ==============================================
goal(Board) :-
    \+ find_empty(Board, _).

% Transição de Estado: s(Estado, ProximoEstado, Custo)
s(Board, NextBoard, 1) :-
    find_empty(Board, [Row, Col]),
    between(1, 9, Value),
    valid(Board, [Row, Col, Value]),
    nth0(Row, Board, RowList),
    replace(RowList, Col, Value, NewRowList),
    replace(Board, Row, NewRowList, NextBoard).

% A nossa Heurística (h): Baseia-se no nº de casas vazias
h(Board, H) :-
    findall(_, find_empty(Board, _), Empties),
    length(Empties, H).

% bestfirst(Start, Solution): Solution is a path from Start to a goal
bestfirst(Start, Solution) :-
    expand([], l(Start, 0/0), 9999, _, yes, Solution). % Assume 9999 is > any f-value

% expand( Path, Tree, Bound, Treel, Solved, Solution):
expand(P, l( N, _), _, _, yes, [N | P]) :-
    goal(N).

expand(P, l(N, F/G), Bound, Tree1, Solved, Sol) :-
    F =< Bound,
    ( bagof( M/C, ( s(N, M, C), \+ member(M, P)), Succ),
    !,                      % Node N has successors
    succlist( G, Succ, Ts), % Make subtrees Ts
    bestf( Ts, F1),         % f-value of best successor
    expand( P, t(N, F1/G, Ts), Bound, Tree1, Solved, Sol)
    ;
    Solved = never           % N has no successors - dead end
  ).

expand( P, t(N, F/G, [T | Ts]), Bound, Tree1, Solved, Sol) :-
    F =< Bound,
    bestf(Ts, BF), Bound1 is min(Bound, BF), % NOTA: O professor avisou no guião que min() com 3 argumentos não funciona no SWI, convertemos para `is min()`
    expand( [N | P], T, Bound1, T1, Solved1, Sol),
    continue( P, t(N, F/G, [T1 | Ts]), Bound, Tree1, Solved1, Solved, Sol).

expand( _, t(_, _, []), _, _, never, _) :- !.

expand( _, Tree, Bound, Tree, no, _) :-
    f( Tree, F), F > Bound.

continue( _,_,_,_, yes, yes, Sol).

continue( P, t(N, F/G, [T1 | Ts]), Bound, Tree1, no, Solved, Sol) :-
    insert( T1, Ts, NTs),
    bestf( NTs, F1),
    expand( P, t(N, F1/G, NTs), Bound, Tree1, Solved, Sol).

continue( P, t(N, F/G, [_ | Ts]), Bound, Tree1, never, Solved, Sol) :-
    bestf( Ts, F1),
    expand( P, t(N, F1/G, Ts), Bound, Tree1, Solved, Sol).

succlist( _, [], []).

succlist( GO, [N/C | NCs], Ts) :-
    G is GO + C,
    h( N, H),     % Heuristic term h(N)
    F is G + H,
    succlist( GO, NCs, Ts1),
    insert( l(N, F/G), Ts1, Ts).

insert( T, Ts, [T | Ts]) :-
    f( T, F), bestf( Ts, F1),
    F =< F1, !.

insert( T, [T1 | Ts], [T1 | Ts1]) :-
    insert( T, Ts, Ts1).

f( l(_, F/_), F).        % f-value of a leaf
f( t(_, F/_, _), F).     % f-value of a tree

bestf( [T | _], F) :-    % Best f-value of a list of trees
    f( T, F).

bestf( [], 9999).         % No trees: bad f-value