:- module(iterative_deepening, [depth_first_iterative_deepening/2]).

:- use_module('../logic/operators').
:- consult('path.pl').

% ==============================================
% LIGAÇÃO AO SUDOKU
% ==============================================
goal(Board) :-
    \+ find_empty(Board, _).

% Transição de transição s(EstadoAtual, ProximoEstado)
s(Board, NextBoard) :-
    find_empty(Board, [Row, Col]),
    between(1, 9, Value),
    valid(Board, [Row, Col, Value]),
    nth0(Row, Board, RowList),
    replace(RowList, Col, Value, NewRowList),
    replace(Board, Row, NewRowList, NextBoard).

depth_first_iterative_deepening( Node, Solution) :-
    path( Node, GoalNode, Solution),
    goal( GoalNode).