:- use_module('../logic/operators').
:- use_module('../logic/search_stats').

% For Sudoku, every transition fills exactly one empty cell. Therefore, the
% useful solution depth is known in advance: the number of empty cells.
path(Start, Goal, ReversedPath) :-
    empty_count(Start, Depth),
    depth_limited_path(Start, Goal, ForwardPath, Depth),
    reverse(ForwardPath, ReversedPath).

depth_limited_path(Node, Node, [Node], 0).

depth_limited_path(Node, Goal, [Node|Path], Depth) :-
    Depth > 0,
    inc_expanded,
    s(Node, Next),
    Depth1 is Depth - 1,
    depth_limited_path(Next, Goal, Path, Depth1).
