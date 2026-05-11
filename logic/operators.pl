:- module(operators, [
    find_empty/2,
    candidate_values/3,
    constraint_pressure/2,
    dead_end/1,
    empty_count/2,
    valid/2,
    replace/4
]).

:- use_module(board).

% find_empty/2: Encontra a celula vazia com menos valores possiveis.
find_empty(Board, [Row, Col]) :-
    findall(Count-RowIndex-ColIndex,
            (   empty_cell(Board, [RowIndex, ColIndex]),
                candidate_values(Board, [RowIndex, ColIndex], Values),
                length(Values, Count)
            ),
            Options),
    sort(Options, [_-Row-Col|_]).

empty_cell(Board, [Row, Col]) :-
    nth0(Row, Board, RowList),
    nth0(Col, RowList, Elem),
    var(Elem).

candidate_values(Board, [Row, Col], Values) :-
    findall(Value,
            (   between(1, 9, Value),
                valid(Board, [Row, Col, Value])
            ),
            Values).

dead_end(Board) :-
    empty_cell(Board, [Row, Col]),
    candidate_values(Board, [Row, Col], []).

constraint_pressure(Board, Pressure) :-
    findall(CellPressure,
            (   empty_cell(Board, [Row, Col]),
                candidate_values(Board, [Row, Col], Values),
                length(Values, Count),
                CellPressure is 9 - Count
            ),
            Pressures),
    sum_list(Pressures, Pressure).

empty_count(Board, Count) :-
    findall(_, empty_cell(Board, _), EmptyCells),
    length(EmptyCells, Count).

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
