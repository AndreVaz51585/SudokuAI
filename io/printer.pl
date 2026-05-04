:- module(printer, [print_board/1]).

% print_board/1: Imprime o tabuleiro.
print_board([]) :- nl.
print_board([Row|Rows]) :-
    print_row(Row),
    print_board(Rows).

print_row([]) :- nl.
print_row([Cell|Cells]) :-
    (   var(Cell) -> write('_')
    ;   write(Cell)
    ),
    write(' '),
    print_row(Cells).

