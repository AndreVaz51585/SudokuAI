:- module(a_star, [bestfirst/2]).

:- use_module('../logic/operators').
:- use_module('../logic/search_stats').

goal(Board) :-
    empty_count(Board, 0).

% Transicao de Estado: s(Estado, ProximoEstado, Custo)
s(Board, NextBoard, 1) :-
    find_empty(Board, [Row, Col]),
    candidate_values(Board, [Row, Col], Values),
    order_values(Board, Row, Col, Values, OrderedValues),
    member(Value, OrderedValues),
    nth0(Row, Board, RowList),
    replace(RowList, Col, Value, NewRowList),
    replace(Board, Row, NewRowList, NextBoard),
    \+ dead_end(NextBoard),
    inc_generated.

% A heuristica continua admissivel: nunca ultrapassa o numero de casas
% vazias, que e o custo minimo restante quando cada acao preenche uma celula.
% A componente fracionaria funciona como desempate e prefere estados mais
% constrangidos, evitando que todos os ramos tenham exatamente o mesmo f.
h(Board, H) :-
    empty_count(Board, Empty),
    (   Empty =:= 0
    ->  H = 0
    ;   constraint_pressure(Board, Pressure),
        MaxPressure is max(1, Empty * 8),
        TieBreak is Pressure / (MaxPressure + 1),
        H is Empty - TieBreak
    ).

order_values(_, _, _, [], []).
order_values(Board, Row, Col, Values, OrderedValues) :-
    findall(Score-Value,
            (   member(Value, Values),
                nth0(Row, Board, RowList),
                replace(RowList, Col, Value, NewRowList),
                replace(Board, Row, NewRowList, CandidateBoard),
                (   dead_end(CandidateBoard)
                ->  Score = -1
                ;   constraint_pressure(CandidateBoard, Score)
                )
            ),
            ScoredValues),
    keysort(ScoredValues, Ascending),
    reverse(Ascending, Descending),
    findall(Value, member(_-Value, Descending), OrderedValues).

% bestfirst(Start, Solution): Solution is a path from Start to a goal
bestfirst(Start, Solution) :-
    expand([], l(Start, 0/0), 9999, _, yes, Solution).

% expand(Path, Tree, Bound, Treel, Solved, Solution)
expand(P, l(N, _), _, _, yes, [N | P]) :-
    goal(N).

expand(P, l(N, F/G), Bound, Tree1, Solved, Sol) :-
    F =< Bound,
    inc_expanded,
    (   bagof(M/C, (s(N, M, C), not_member_eq(M, P)), Succ)
    ->  succlist(G, Succ, Ts),
        bestf(Ts, F1),
        expand(P, t(N, F1/G, Ts), Bound, Tree1, Solved, Sol)
    ;   Solved = never
    ).

expand(P, t(N, F/G, [T | Ts]), Bound, Tree1, Solved, Sol) :-
    F =< Bound,
    bestf(Ts, BF),
    Bound1 is min(Bound, BF),
    expand([N | P], T, Bound1, T1, Solved1, Sol),
    continue(P, t(N, F/G, [T1 | Ts]), Bound, Tree1, Solved1, Solved, Sol).

expand(_, t(_, _, []), _, _, never, _) :- !.

expand(_, Tree, Bound, Tree, no, _) :-
    f(Tree, F),
    F > Bound.

continue(_, _, _, _, yes, yes, _).

continue(P, t(N, _/G, [T1 | Ts]), Bound, Tree1, no, Solved, Sol) :-
    insert(T1, Ts, NTs),
    bestf(NTs, F1),
    expand(P, t(N, F1/G, NTs), Bound, Tree1, Solved, Sol).

continue(P, t(N, _/G, [_ | Ts]), Bound, Tree1, never, Solved, Sol) :-
    bestf(Ts, F1),
    expand(P, t(N, F1/G, Ts), Bound, Tree1, Solved, Sol).

succlist(_, [], []).

succlist(G0, [N/C | NCs], Ts) :-
    G is G0 + C,
    h(N, H),
    F is G + H,
    succlist(G0, NCs, Ts1),
    insert(l(N, F/G), Ts1, Ts).

insert(T, Ts, [T | Ts]) :-
    f(T, F),
    bestf(Ts, F1),
    F =< F1, !.

insert(T, [T1 | Ts], [T1 | Ts1]) :-
    insert(T, Ts, Ts1).

f(l(_, F/_), F).
f(t(_, F/_, _), F).

bestf([T | _], F) :-
    f(T, F).

bestf([], 9999).

not_member_eq(_, []).
not_member_eq(Node, [Visited|Rest]) :-
    Node \== Visited,
    not_member_eq(Node, Rest).
