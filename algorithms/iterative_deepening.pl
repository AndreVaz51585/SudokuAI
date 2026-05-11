:- module(iterative_deepening, [depth_first_iterative_deepening/2]).

:- use_module('../logic/operators').
:- use_module('../logic/search_stats').
:- consult('path.pl').

goal(Board) :-
    empty_count(Board, 0).

% Transição de transição s(EstadoAtual, ProximoEstado)
s(Board, NextBoard) :-
    find_empty(Board, [Row, Col]),
    candidate_values(Board, [Row, Col], Values),
    member(Value, Values),
    nth0(Row, Board, RowList),
    replace(RowList, Col, Value, NewRowList),
    replace(Board, Row, NewRowList, NextBoard),
    inc_generated.

depth_first_iterative_deepening( Node, Solution) :-
    path( Node, GoalNode, Solution),
    goal( GoalNode).
