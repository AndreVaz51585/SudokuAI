:- module(operators, [
    find_empty/2,
    valid/2,
    replace/4
]).

:- use_module(board).

% find_empty/2: Encontra a proxima celula vazia no tabuleiro.
find_empty(Board, [Row, Col]) :-
    nth0(Row, Board, RowList), 
    nth0(Col, RowList, Elem),
    var(Elem), !.

% valid/2: Valida se um valor pode ser colocado sem violar as regras do Sudoku.
valid(Board, [Row, Col, Value]) :-
    get_row(Board, Row, RowList),
    \+ (member(X1, RowList), nonvar(X1), X1 == Value),
    get_col(Board, Col, ColList),
    \+ (member(X2, ColList), nonvar(X2), X2 == Value),
    get_subgrid(Board, Row, Col, Subgrid),
    \+ (member(X3, Subgrid), nonvar(X3), X3 == Value).

% replace/4: Substitui um elemento numa lista pelo indice
replace([_|T], 0, X, [X|T]).
replace([H|T], I, X, [H|R]) :-
    I > 0,
    I1 is I - 1,
    replace(T, I1, X, R).