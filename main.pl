:- module(main, [solve/1, solve/2]).

:- use_module('logic/board').
:- use_module('logic/operators').
:- use_module('logic/search_stats').
:- use_module('io/printer').
:- use_module('algorithms/iterative_deepening').
:- use_module('algorithms/a_star').

% Example: ?- solve([[5,3,_,_,7,_,_,_,_],[6,_,_,1,9,5,_,_,_],[_,9,8,_,_,_,_,6,_],[8,_,_,_,6,_,_,_,3],[4,_,_,8,_,3,_,_,1],[7,_,_,_,2,_,_,_,6],[_,6,_,_,_,_,2,8,_],[_,_,_,4,1,9,_,_,5],[_, _, _, _, 8, _, _, 7, 9]]).
solve(Puzzle) :-
    write('Select algorithm:'), nl,
    write('1. Iterative Deepening'), nl,
    write('2. A*'), nl,
    read(Choice),
    (   Choice = 1 -> solve(Puzzle, iterative_deepening)
    ;   Choice = 2 -> solve(Puzzle, a_star)
    ;   write('Invalid choice, try again.'), nl,
        solve(Puzzle)
    ).


% solve/2: Solves a Sudoku using a specific algorithm.
% Example: ?- solve([[...]], a_star).
solve(Puzzle, iterative_deepening) :-
    write('Solving with Iterative Deepening...'), nl,
    reset_stats,
    get_time(Start),
    depth_first_iterative_deepening(Puzzle, Path),
    get_time(End),
    Elapsed is End - Start,
    final_board(Path, Solution),
    write('Solution found:'), nl,
    print_board(Solution),
    print_stats(Elapsed).

solve(Puzzle, a_star) :-
    write('Solving with A*...'), nl,
    reset_stats,
    get_time(Start),
    bestfirst(Puzzle, Path),
    get_time(End),
    Elapsed is End - Start,
    final_board(Path, Solution),
    write('Solution found:'), nl,
    print_board(Solution),
    print_stats(Elapsed).

% The search algorithms return a path with the goal state at the head.
final_board([Solution|_], Solution).

