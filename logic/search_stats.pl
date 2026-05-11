:- module(search_stats, [
    reset_stats/0,
    inc_expanded/0,
    inc_generated/0,
    print_stats/1
]).

reset_stats :-
    nb_setval(expanded_states, 0),
    nb_setval(generated_states, 0).

inc_expanded :-
    inc_stat(expanded_states).

inc_generated :-
    inc_stat(generated_states).

inc_stat(Name) :-
    (   nb_current(Name, Value)
    ->  Next is Value + 1
    ;   Next = 1
    ),
    nb_setval(Name, Next).

print_stats(ElapsedSeconds) :-
    stat_value(expanded_states, Expanded),
    stat_value(generated_states, Generated),
    ElapsedMs is ElapsedSeconds * 1000,
    nl,
    write('Search statistics:'), nl,
    format('  Time: ~2f ms~n', [ElapsedMs]),
    format('  Expanded states: ~d~n', [Expanded]),
    format('  Generated states: ~d~n', [Generated]).

stat_value(Name, Value) :-
    (   nb_current(Name, Value)
    ->  true
    ;   Value = 0
    ).
