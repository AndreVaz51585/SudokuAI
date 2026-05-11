# SudokuAI

Solucionador de Sudoku para o segundo trabalho de IA.

## Modos disponíveis

- Prolog: `iterative_deepening` e `a_star`.
- Python: `sa` (Simulated Annealing) e `ga` (Genetic Algorithm).
- Tipos de jogo na CLI Python: `classic` e `killer`.

## Executar

Listar puzzles:

```bash
python sudoku.py --list
```

Resolver um Sudoku clássico com SA:

```bash
python sudoku.py --game classic --algorithm sa --puzzle easy --seed 1
```

Resolver um Sudoku clássico com GA:

```bash
python sudoku.py --game classic --algorithm ga --puzzle easy --seed 1
```

Resolver o exemplo Killer Sudoku:

```bash
python sudoku.py --game killer --algorithm sa --puzzle demo --seed 3
python sudoku.py --game killer --algorithm ga --puzzle demo --seed 3
```

Os algoritmos Prolog são chamados pela mesma CLI se o `swipl` estiver no `PATH`:

```bash
python sudoku.py --game classic --algorithm a_star --puzzle easy
python sudoku.py --game classic --algorithm iterative_deepening --puzzle easy
```

## Benchmark

```bash
python benchmark.py
```

O benchmark imprime CSV com `game,puzzle,algorithm,solved,cost,evaluations,time_ms`.
SA e GA são estocásticos: em puzzles muito difíceis podem ficar em custos baixos sem chegar a custo zero dentro dos limites definidos. Para o relatório, registar também a seed, o número de avaliações e o melhor custo encontrado.

## Heurística A*

A heurística Prolog continua admissível porque nunca ultrapassa o número de casas vazias. Foi acrescentado um desempate fracionário baseado na pressão de restrições das células vazias. Assim, estados com o mesmo número de jogadas restantes deixam de ter todos o mesmo `f = g + h`, e o A* tende a expandir primeiro estados mais constrangidos.

Também foi acrescentada filtragem de sucessores que deixam alguma célula vazia sem candidatos.

## Representação SA/GA

As soluções Python são tabuleiros 9x9 completos. A inicialização preenche cada bloco 3x3 com uma permutação válida dos dígitos em falta, preservando sempre os números fixos. A vizinhança principal troca duas células não fixas dentro do mesmo bloco, mantendo os blocos válidos. A função de custo soma conflitos em linhas e colunas; no Killer Sudoku soma também penalizações de cages.
