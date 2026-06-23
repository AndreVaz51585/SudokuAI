# Relatório - Solucionador de Sudoku e Killer Sudoku

## 1. Informações Gerais

**Unidade Curricular**: Inteligência Artificial (2º Trabalho)  
**Grupo**: Diogo Santos (51846), André Vaz (51585), Diogo Teixeira (50506)
**Data**: Maio 2026

---

## 2. Objetivo

Implementar um solucionador automático para Sudoku clássico e Killer Sudoku comparando quatro algoritmos distintos: Iterative Deepening (ID), A*, Simulated Annealing (SA) e Genetic Algorithm (GA).

---

## 3. Estrutura e Predicados Principais

A implementação divide-se em duas abordagens: pesquisa em Prolog e otimização em Python.

### Predicados Prolog (Pesquisa)

**board.pl**: Define a representação do tabuleiro e validações
- `valid_row/3`: Verifica se linha não tem dígitos duplicados
- `valid_col/3`: Verifica se coluna não tem dígitos duplicados
- `valid_block/3`: Valida bloco 3x3
- `get_candidates/3`: Lista dígitos válidos para uma célula

**operators.pl**: Operadores de transição de estado
- `fill_cell/4`: Preenche uma célula com um dígito
- `next_empty_cell/3`: Localiza próxima célula vazia

**algorithms/iterative_deepening.pl**: Pesquisa com aprofundamento iterativo
- `id_search/4`: Executa DFID com limite de profundidade crescente

**algorithms/a_star.pl**: Pesquisa informada
- `a_star_search/4`: Best-first search com heurística
- `h_value/2`: Heurística baseada em células vazias + pressão de restrições

### Estruturas Python (Otimização)

SA e GA representam o tabuleiro como matriz 9x9 completa. Diferem na inicialização, vizinhança e operadores genéticos.

---

## 4. Decisões de Design Justificadas

### 4.1 Representação Dicotômica
**Decisão**: Prolog usa tabuleiro parcial (pesquisa), Python usa tabuleiro completo (otimização).

**Justificativa**: 
- Pesquisa beneficia de podas em células vazias
- Otimização requer solução completa para avaliar custos
- Vizinhança de SA (swap em bloco) é mais eficaz com tabuleiro preenchido

### 4.2 Heurística A* (Não Admissível Aprimorada)
**Decisão**: h = células_vazias + 0.1 * pressão_restrições

**Justificativa**:
- Número de células vazias é lower bound válido
- Desempate por pressão de restrições acelera convergência sem violar admissibilidade
- Filtragem de sucessores elimina estados inviáveis precocemente

### 4.3 SA vs GA para Otimização
**Decisão**: SA e GA foram incluídos como técnicas de otimização estocástica para comparação com os algoritmos de pesquisa.

**Justificativa**:
- SA tem overhead menor, porque trabalha com uma solução corrente e um vizinho de cada vez
- GA explora múltiplas regiões do espaço através de uma população de soluções
- Nos testes medidos, ambos resolvem o puzzle easy, mas o SA é substancialmente mais rápido
- Em puzzles mais difíceis, nenhum dos dois garante solução dentro dos limites definidos

### 4.4 Vizinhança de SA (Swap em Bloco)
**Decisão**: Trocar apenas células mutáveis dentro do mesmo bloco 3x3.

**Justificativa**:
- Mantém validação automática de blocos após cada move
- Reduz espaço de exploração sem sacrificar qualidade
- Vizinhança conectada garante convergência local

---

## 5. Resultados Experimentais

### 5.1 Sudoku Clássico - Desempenho Temporal

Os resultados Python foram obtidos pela CLI com `--seed 1` e os parâmetros por
defeito de cada algoritmo. Os resultados Prolog foram obtidos no SWI-Prolog.

| Puzzle | Algoritmo | Resolvido | Custo final | Avaliações/Estados | Restarts/Gerações | Tempo (ms) |
|--------|-----------|-----------|-------------|--------------------|-------------------|------------|
| Easy | ID | Sim | - | 51 estados expandidos / 51 gerados | - | 74.12 |
| Easy | A* | Sim | - | 51 estados expandidos / 51 gerados | - | 259.76 |
| Easy | SA | Sim | 0 | 49 926 avaliações | 1 restart | 734.03 |
| Easy | GA | Sim | 0 | 83 700 avaliações | 464 gerações | 11 055.89 |
| Hard Norvig | ID | Sim | - | 10 101 estados expandidos / 10 101 gerados | - | 13 760.29 |
| Hard Norvig | A* | Sim | - | 17 136 estados expandidos / 17 136 gerados | - | 119 344.39 |
| Hard Norvig | SA | Não | 2 | 5 000 040 avaliações | 20 restarts | 73 002.27 |
| Hard Norvig | GA | Não | 2 | 2 160 720 avaliações | 12 000 gerações | 286 106.70 |
| Very Hard / AI Escargot | ID | Sim | - | 217 estados expandidos / 217 gerados | - | 262.07 |
| Minimal 17 clues | ID | Sim | - | 4 835 estados expandidos / 4 835 gerados | - | 6 835.54 |

**Análise**: No puzzle `easy`, todos os algoritmos testados encontram a solução.
O ID é o mais rápido neste caso, com 74.12 ms, seguido do A* com 259.76 ms. O SA
também encontra custo 0, mas precisa de 49 926 avaliações. O GA resolve o mesmo
puzzle, mas demora 11 055.89 ms, cerca de 15.1x mais tempo do que o SA, porque
precisa de avaliar uma população durante 464 gerações.

No puzzle `hard_norvig`, os dois algoritmos Prolog encontram solução. Neste
caso, o ID é mais rápido, demorando 13 760.29 ms e expandindo 10 101 estados,
enquanto o A* demora 119 344.39 ms e expande 17 136 estados. O SA e o GA
terminam ambos com custo 2, não encontrando uma solução válida dentro dos
limites configurados. O SA percorre os 20 restarts definidos por defeito e
termina em 73 002.27 ms. O GA executa as 12 000 gerações resultantes das 4 runs
de 3 000 gerações e demora 286 106.70 ms, cerca de 3.9x mais tempo que o SA.
Isto mostra a principal limitação da abordagem por otimização: mesmo reduzindo
bastante os conflitos, os algoritmos podem ficar presos perto de uma solução sem
atingir custo 0.

Nos puzzles `very_hard_ai_escargot` e `minimal_17_clues`, foram medidos
resultados adicionais com ID. O ID resolveu o `very_hard_ai_escargot` em
262.07 ms, expandindo apenas 217 estados, e resolveu o `minimal_17_clues` em
6 835.54 ms, expandindo 4 835 estados. Estes resultados mostram que a escolha da
célula com menos candidatos reduz muito o espaço de pesquisa nestes exemplos.

### 5.2 Killer Sudoku - Desempenho Temporal

Os resultados seguintes foram obtidos com `--seed 3`.

| Puzzle | Algoritmo | Resolvido | Custo final | Avaliações | Restarts/Gerações | Tempo (ms) |
|--------|-----------|-----------|-------------|------------|-------------------|------------|
| Demo | SA | Sim | 0 | 31 888 | 1 restart | 750.17 |
| Demo | GA | Sim | 0 | 3 600 | 19 gerações | 758.31 |

**Análise**: No Killer Sudoku `demo`, tanto SA como GA encontram a solução
correta com custo 0. Os tempos são praticamente equivalentes: SA demora
750.17 ms e GA demora 758.31 ms. O GA precisa de muito menos avaliações diretas
do que o SA, mas cada geração envolve operações adicionais de seleção, crossover
e mutação, o que faz com que o tempo final fique muito próximo.

### 5.3 Taxa de Sucesso

| Algoritmo | Easy | Hard Norvig | Very Hard | Minimal 17 | Killer Demo |
|-----------|------|-------------|-----------|------------|-------------|
| ID        | Sim  | Sim         | Sim       | Sim        | N/A         |
| A*        | Sim  | Sim         | Por medir | Por medir  | N/A         |
| SA        | Sim  | Não, custo 2 | Por medir | Por medir | Sim         |
| GA        | Sim  | Não, custo 2 | Por medir | Por medir | Sim         |

**Análise**: Com os dados atualmente medidos, todos os algoritmos testados
resolvem o puzzle `easy`. No `hard_norvig`, ID e A* encontram solução, enquanto
SA e GA aproximam-se da solução mas terminam com custo 2, ou seja, ainda existem
conflitos no tabuleiro final. O ID também resolveu os puzzles
`very_hard_ai_escargot` e `minimal_17_clues`. No Killer Sudoku `demo`, os dois
algoritmos Python resolvem o puzzle.

### 5.4 Eficiência Computacional

- **SA no easy**: 49 926 avaliações / 734.03 ms = 68.02 avaliações/ms
- **SA no hard_norvig**: 5 000 040 avaliações / 73 002.27 ms = 68.49 avaliações/ms
- **GA no easy**: 83 700 avaliações / 11 055.89 ms = 7.57 avaliações/ms
- **GA no hard_norvig**: 2 160 720 avaliações / 286 106.70 ms = 7.55 avaliações/ms
- **Razão no easy**: SA executa cerca de 9.0x mais avaliações por ms do que GA
- **Razão no hard_norvig**: SA executa cerca de 9.1x mais avaliações por ms do que GA

Apesar de ambos seguirem a estrutura dos algoritmos do professor, o GA tem mais
overhead por trabalhar com uma população completa, seleção, crossover e mutação
em cada geração. O SA trabalha apenas com uma solução corrente e um vizinho de
cada vez, o que explica a maior taxa de avaliações por milissegundo.

---

## 6. Comparação de Algoritmos

### A* (Prolog)
- **Vantagem**: Determinístico e completo nos casos medidos
- **Desvantagem**: Pode demorar bastante em puzzles difíceis; no hard_norvig foi mais lento que ID
- **Uso recomendado**: Aplicações interativas, puzzles fáceis a médios

### SA (Python)
- **Vantagem**: Baixo overhead por iteração; resolve o puzzle easy e o Killer demo
- **Desvantagem**: Estocástico, não garante ótimo global; no hard_norvig ficou em custo 2
- **Uso recomendado**: Demonstração de otimização local/estocástica e comparação com pesquisa

### GA (Python)
- **Vantagem**: Explora múltiplas regiões do espaço através de uma população; resolve o easy e o Killer demo
- **Desvantagem**: Muito mais lento que SA; no hard_norvig também ficou em custo 2
- **Uso recomendado**: Demonstração da adaptação de seleção, crossover e mutação ao Sudoku

### ID (Prolog)
- **Vantagem**: Muito rápido nos puzzles Prolog medidos, incluindo hard_norvig, very_hard_ai_escargot e minimal_17_clues
- **Desvantagem**: Pode crescer exponencialmente em puzzles mais difíceis
- **Uso recomendado**: Análise teórica

---

## 7. Conclusões

1. **Os algoritmos Prolog são preferíveis quando se pretende determinismo**, porque fazem pesquisa construtiva e encontraram solução nos casos medidos; neste conjunto de testes, o ID foi o mais forte entre os algoritmos de pesquisa.

2. **Simulated Annealing tem menor overhead que GA**, executando cerca de 9.0x mais avaliações por ms no puzzle easy.

3. **Genetic Algorithm resolve o puzzle easy**, mas demora cerca de 15.1x mais tempo que SA no mesmo puzzle; no hard_norvig também termina com custo 2.

4. **Heurística admissível com desempate** acelera A* sem violar otimalidade.

5. **Vizinhança compacta (swap em bloco)** é chave para eficiência de SA.

**Recomendação final**: Usar A* em contextos onde velocidade e determinismo são críticos; usar SA e GA como comparação de técnicas de otimização estocástica adaptadas ao Sudoku, tendo em conta que não garantem solução em puzzles difíceis dentro dos limites definidos.
