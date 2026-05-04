:- module(board, [
    sudoku/1,
    get_row/3,
    get_col/3,
    get_subgrid/4
]).
% permite definir e manipular tabuleiros de Sudoku
% propaga as restrições do Sudoku usando o CLP(FD) para garantir que as soluções sejam válidas.
% reduz o espaço de busca
:- use_module(library(clpfd)).

% sudoku/1: define e resolve o sudoku
% Rows é uma lista de 9 listas representando as linhas do tabuleiro. Cada elemento pode ser um número de 1 a 9 ou uma variável (representando uma célula vazia).

sudoku(Rows) :-
    length(Rows, 9),    % garante que há 9 linhas
    maplist(same_length(Rows), Rows), % todas as linhas têm o mesmo comprimento (9 colunas)
    append(Rows, Vs), % junta todas as listas numa só lista.
    Vs ins 1..9, % cada célula deve conter um número de 1 a 9
    maplist(all_distinct, Rows),% cada linha não pode conter números repetidos
    transpose(Rows, Columns), % converte linhas em colunas.
    maplist(all_distinct, Columns), % cada coluna não pode conter números repetidos
    Rows = [A,B,C,D,E,F,G,H,I], % define as linhas do tabuleiro com letras 
    blocks(A,B,C), blocks(D,E,F), blocks(G,H,I). % cada grupo de 3 linhas forma um bloco 3x3, e cada bloco não pode conter números repetidos

    % [A][B][C]
    % [D][E][F]
    % [G][H][I]


% responsável por transformar as linhas do tabuleiro em blocos 3x3 e garantir que cada bloco contenha números distintos.
blocks([], [], []).

blocks([N1,N2,N3|T1], [N4,N5,N6|T2], [N7,N8,N9|T3]) :-
    all_distinct([N1,N2,N3,N4,N5,N6,N7,N8,N9]),
    blocks(T1, T2, T3).

% get_row/3: Obtem uma linha específica do tabuleiro.
get_row(Board, RowIndex, Row) :-
    nth0(RowIndex, Board, Row).

% get_col/3: Obtem uma coluna específica do tabuleiro.
get_col(Board, ColIndex, Column) :-
    transpose(Board, Transposed), % transpoe o tabuleiro para facilitar a obtenção da coluna
    nth0(ColIndex, Transposed, Column).

% get_subgrid/4: Obtem um subgrid 3x3 do tabuleiro com base nos índices de linha e coluna.
get_subgrid(Board, Row, Col, Subgrid) :-
    SubgridRow is Row // 3,
    SubgridCol is Col // 3,
    findall(E,
            (   between(0, 2, I),
                between(0, 2, J),
                RowIdx is SubgridRow * 3 + I,
                ColIdx is SubgridCol * 3 + J,
                nth0(RowIdx, Board, R),
                nth0(ColIdx, R, E)
            ),
            Subgrid).
