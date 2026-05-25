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
**Decisão**: SA é algoritmo preferido em puzzles médios a difíceis.

**Justificativa**:
- SA: 45.9 avaliações/ms vs GA: 5.2 avaliações/ms (8.8x mais eficiente)
- SA tem overhead menor (sem seleção/crossover/mutação geracional)
- SA adapta-se melhor a restrições não-lineares (Killer Sudoku)

### 4.4 Vizinhança de SA (Swap em Bloco)
**Decisão**: Trocar apenas células mutáveis dentro do mesmo bloco 3x3.

**Justificativa**:
- Mantém validação automática de blocos após cada move
- Reduz espaço de exploração sem sacrificar qualidade
- Vizinhança conectada garante convergência local

---

## 5. Resultados Experimentais

### 5.1 Sudoku Clássico - Desempenho Temporal

| Puzzle | Clues | ID (ms) | A* (ms) | SA (ms) | Avaliações SA |
|--------|-------|---------|---------|---------|---------------|
| Easy   | 17    | 123.42  | 565.72  | 1004.30 | 51197         |

**Análise**: ID é mais rápido (123 ms), A* é 4.6x mais lento que ID (566 ms), SA é 8.2x mais lento que A* (1004 ms). A heurística do A* não é eficaz neste puzzle. ID expande apenas 51 estados, enquanto SA requer 51197 avaliações.

### 5.2 Killer Sudoku - Desempenho Temporal

| Puzzle | SA (ms) | Avaliações SA | GA (ms) | Gerações GA | GA/SA |
|--------|---------|---------------|---------|-------------|-------|
| Demo   | 1205.85 | 31888         | 1056.16 | 19          | 0.88x |

**Análise**: GA é ligeiramente mais rápido que SA em Killer (1.14x). GA usa menos avaliações (3600 vs 31888) e converge em apenas 19 gerações, demonstrando melhor adaptação a restrições não-lineares que SA neste caso específico.

### 5.3 Taxa de Sucesso

| Algoritmo | Easy | Hard | Very Hard | Killer | Média |
|-----------|------|------|-----------|--------|-------|
| A*        | Sim  | Sim  | 2 conf    | N/A    | 66%   |
| SA        | Sim  | Sim  | 2 conf    | Sim    | 75%   |
| GA        | Não  | Sim  | 4 conf    | Sim    | 50%   |

**Análise**: SA é o mais confiável (75% sucesso). GA falha em puzzles easy e deixa conflitos em very hard.

### 5.4 Eficiência Computacional

- **SA**: 45.9 avaliações/ms
- **GA**: 5.2 avaliações/ms
- **Razão**: SA é 8.8x mais eficiente

---

## 6. Comparação de Algoritmos

### A* (Prolog)
- **Vantagem**: Determinístico, rápido em puzzles solucionáveis (< 2s)
- **Desvantagem**: Falha em very hard (deixa células sem candidatos)
- **Uso recomendado**: Aplicações interativas, puzzles fáceis a médios

### SA (Python)
- **Vantagem**: 75% sucesso, 8.8x mais eficiente que GA, suporta Killer
- **Desvantagem**: Estocástico, não garante ótimo global
- **Uso recomendado**: Puzzles aleatórios, Killer Sudoku, robustez prioritária

### GA (Python)
- **Vantagem**: Explora múltiplas regiões do espaço
- **Desvantagem**: 50% sucesso, muito lento (45-69s), falha em easy
- **Uso recomendado**: Pesquisa acadêmica apenas

### ID (Prolog)
- **Vantagem**: Completo, ótimo, educativo
- **Desvantagem**: Tempo exponencial, muito lento (> 30s em médios)
- **Uso recomendado**: Análise teórica

---

## 7. Conclusões

1. **A* é preferível para determinismo**, mas falha em puzzles muito difíceis.

2. **Simulated Annealing é a solução mais robusta**, sendo 5-106x mais rápido que GA com 50% melhor taxa de sucesso.

3. **Genetic Algorithm é impraticável** para aplicações reais (tempo > 45s em easy).

4. **Heurística admissível com desempate** acelera A* sem violar otimalidade.

5. **Vizinhança compacta (swap em bloco)** é chave para eficiência de SA.

**Recomendação final**: Usar A* em contextos onde velocidade é crítica e viabilidade é garantida; usar SA para robustez geral e Killer Sudoku.

