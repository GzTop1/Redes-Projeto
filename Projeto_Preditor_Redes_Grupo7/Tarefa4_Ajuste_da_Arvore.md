# Diário da Tarefa 4 — Ajuste do modelo a partir do erro

**Período:** 05/10/2026 a 11/10/2026  
**Projeto:** Preditor de degradação de rede relativo ao baseline do fluxo (independente da rota)

**Equipe:** Grupo 7  
**Scrum Master da tarefa:** Hendrick Ambriola  
**Repositório GitHub:** https://github.com/GzTop1/Redes-Projeto
>
> O rótulo, o baseline e o corte da Tarefa 2 continuam. País, IP, rota e RTT absoluto continuam fora.

### Contrato desta tarefa

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Árvore da Tarefa 3, matriz e erros | Tarefa 3 |
| **Entra** | Mesmo baseline, mesmo rótulo, mesmo corte | Tarefa 2 |
| **Sai** | Modelo ajustado (`modelos/modelo_T4.joblib`) e tabela T3 → T4 (`tabela_T3_T4.csv`) | Tarefa 5 |
| **Sai** | Registro de todos os candidatos (`grade_busca.csv`) | Tarefa 5 |
| **Sai** | Dicionário v0.3 | Tarefa 5 |

**Não sai daqui:** mudança do teste, recálculo do baseline com o Período B.

- [x] O corte é o da Tarefa 2
- [x] Nenhuma coluna de rota entrou

---

## 1. O que o erro pediu

- [x] Erros da Tarefa 3 citados
- [x] Cada mudança responde a um desses erros
- [x] Parâmetros escolhidos na validação

Diagnóstico da árvore da Tarefa 3 na validação:
- Confusão dominante: **RISCO real previsto como OK** (1.990 casos).
- Recall de RISCO 0,4213; recall de FALHA 0,7046.
- **87,4%** dos erros acontecem quando a classe muda de t para t+1.
- Gap treino−validação: 0,0233.

**Erro da Tarefa 3 → mudança testada (uma por vez, sobre a árvore da T3):**

| Erro observado | Mudança | F1 macro (validação) | Δ vs T3 | Recall FALHA | Recall RISCO | Folhas |
|---|---|---|---|---|---|---|
| Recall de RISCO baixo | Critério **entropia** | 0,7675 | −0,0016 | 0,7099 | 0,4160 | 295 |
| RISCO → OK dominante; folhas pequenas podem decorar o treino | `min_samples_leaf` 500 | 0,7671 | −0,0020 | 0,7079 | 0,4293 | 107 |
| Erros nas transições | Mais profundidade (`max_depth` None) | 0,7691 | 0,0000 | 0,7046 | 0,4213 | 1.453 |
| Gap treino−validação | Poda `ccp_alpha` = 0,0005 | 0,7602 | −0,0090 | 0,7079 | 0,3901 | 7 |
| RISCO → OK dominante (desbalanceamento) | `class_weight` balanced | 0,6828 | −0,0863 | **0,7616** | **0,5657** | 299 |
| Erros nas transições | Outras famílias (Naive Bayes, Random Forest) | ver abaixo | | | | |

Nenhuma mudança isolada na árvore superou o F1 macro da Tarefa 3. A mais profunda empatou com 1.453 folhas; pela regra de desempate, a árvore de 220 folhas continua preferida. O `class_weight` balanced é a única mudança que melhora os dois recalls, mas custa 0,086 de F1 macro.

**Grade completa das três famílias (treino → validação):**

| Família | Candidatos | Melhor configuração | F1 macro (validação) | Gap |
|---|---|---|---|---|
| Naive Bayes | 4 | `var_smoothing` 1e-3 | 0,5223 | — |
| Árvore de decisão | 30 | `max_depth` 12, `min_samples_leaf` 100 | 0,7691 | 0,0233 |
| **Random Forest** | 24 | 200 árvores, `max_depth` None, `min_samples_leaf` 5, `max_features` sqrt, sem `class_weight` | **0,7702** | 0,0521 |

Pela regra de seleção (maior F1 macro, depois menor gap), o escolhido é o **Random Forest**.

## 2. Modelo ajustado

- [x] Mesmas 21 variáveis relativas (nenhuma coluna nova)
- [x] Parâmetros registrados
- [x] Fit só no treino
- [ ] Três regras em português: **não se aplica** ao Random Forest (200 árvores). As regras legíveis continuam sendo as da árvore da Tarefa 3.

**Parâmetros:** `RandomForestClassifier`, `n_estimators` 200, `max_depth` None, `min_samples_leaf` 5, `max_features` sqrt, `class_weight` None, `random_state` 42.

## 3. Comparação na validação

| Modelo | F1 macro | Recall FALHA | Recall RISCO | F1 macro (transições) | Recall FALHA (início de falha) |
|---|---|---|---|---|---|
| Persistência (classe atual) | 0,7261 | 0,7341 | 0,4975 | 0,0000 | 0,0000 |
| T3: árvore | 0,7691 | 0,7046 | 0,4213 | 0,2122 | 0,0049 |
| T4: Random Forest | 0,7702 | 0,7073 | 0,4190 | 0,2192 | 0,0074 |

- [x] Matriz 3×3 do modelo desta tarefa, na validação

| | prev. OK | prev. RISCO | prev. FALHA |
|---|---|---|---|
| **real OK** | 35.367 | 83 | 80 |
| **real RISCO** | 1.991 | 1.506 | 97 |
| **real FALHA** | 335 | 112 | 1.080 |

| Classe | Precisão | Recall | F1 |
|---|---|---|---|
| OK | 0,9383 | 0,9954 | 0,9660 |
| RISCO | 0,8854 | 0,4190 | 0,5688 |
| FALHA | 0,8592 | 0,7073 | 0,7759 |

**Leitura do ganho:** de T3 para T4, o ganho é de **+0,0011** em F1 macro, dentro do que se espera de variação entre modelos. O Random Forest também tem gap maior (0,052 contra 0,023). Contra a persistência, os dois modelos ganham cerca de +0,044, porque erram menos ao manter a classe. Mas nenhum dos dois resolve o erro principal: nas transições o F1 macro fica em cerca de 0,21, e quase nenhum início de FALHA é antecipado. A persistência tem até recall de FALHA maior (0,734) que os modelos; a vantagem deles está na precisão.

## 4. Revisão com o docente

**O que foi mostrado:** _(preencher)_  
**O que foi pedido para ajustar antes da Tarefa 5:** _(preencher)_

### Dicionário de dados v0.3

As **variáveis não mudam** (as mesmas 21 da v0.2). Entram os artefatos do modelo:

| Artefato | Conteúdo |
|---|---|
| `grade_busca.csv` | uma linha por candidato: família, parâmetros, F1 macro de treino e validação, gap, recalls |
| `modelo_T4.joblib` | modelo escolhido, lista de variáveis, família e parâmetros |
| `tabela_T3_T4.csv` | persistência, T3 e T4 lado a lado |

Continuam proibidos: país, IP, rota, `id_fluxo` e RTT absoluto.

## 5. Scrum e diário

- [X] Board atualizado

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Isaac William Braz | Não atuei diretamente nesta tarefa (responsável: Hendrick). | — | — |
| Fernanda Akemi Martins Sanpei | Não atuei diretamente nesta tarefa (responsável: Hendrick). | — | — |
| Geziel de Andrade | Não atuei diretamente nesta tarefa (responsável: Hendrick). | — | — |
| Hendrick Ambriola | Diagnóstico dos erros da T3; experimentos com uma mudança por vez (entropia, folha mínima, profundidade, poda, `class_weight`); grade completa de Naive Bayes, árvore e Random Forest; tabela T3 → T4; dicionário v0.3. | Ligar cada mudança a um erro. Aceitar que nenhuma mudança da árvore trouxe ganho. | Manter a escolha só pela validação e apresentar o que foi descartado. |
| Davi Gabriel Borges dos Santos | Não atuei diretamente nesta tarefa (responsável: Hendrick). | — | — |
| Victor Gabriel Alves | Não atuei diretamente nesta tarefa (responsável: Hendrick). | — | — |

**Link do board:** _https://github.com/users/GzTop1/projects/1_

---

## Rubrica — Tarefa 4 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Ajuste ligado ao erro | 1,5 | Cada mudança da árvore cita um erro da Tarefa 3; continua árvore de decisão | | |
| Rota fora do modelo | 1,0 | Nenhuma coluna de rota, país, IP ou RTT absoluto; baseline da Tarefa 2 intacto | | |
| Tabela Tarefa 3 → Tarefa 4 | 1,0 | F1 macro e recall de FALHA e de RISCO na validação, com leitura | | |
| Revisão + diário | 0,5 | Incremento mostrado ao docente; diário de todos | | |
| **Total** | **4,0** | | **___ / 4,0** | |
