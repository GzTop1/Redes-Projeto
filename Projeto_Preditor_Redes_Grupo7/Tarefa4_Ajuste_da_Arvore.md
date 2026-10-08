# Diário da Tarefa 4 — Ajuste da árvore a partir do erro

**Período:** 05/10/2026 a 11/10/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)

**Equipe:** Grupo 7  
**Scrum Master da tarefa:** Hendrick Ambriola  
**Repositório GitHub:** https://github.com/GzTop1/Redes-Projeto

> O rótulo e o baseline da Tarefa 2 continuam. O corte temporal continua. Esta tarefa **não troca o algoritmo**: ajusta a mesma árvore de decisão com o que a Tarefa 3 errou.
>
> Ajuste permitido: profundidade, mínimo de amostras na folha, critério (Gini ou entropia) e poda. Se entrar coluna nova, ela tem de ser outra métrica **relativa ao baseline** (tendência do `z_robusto` nas janelas anteriores, por exemplo). País, IP, rota e RTT absoluto continuam fora.

### Contrato desta tarefa

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Árvore da Tarefa 3, matriz e erros | Tarefa 3 |
| **Entra** | Mesmo baseline, mesmo rótulo, mesmo corte | Tarefa 2 |
| **Sai** | Árvore ajustada e tabela Tarefa 3 → Tarefa 4 (F1 macro e recall de FALHA na validação) | Tarefa 5 usa **esta** árvore como ponto de partida |
| **Sai** | Regras novas em português | Tarefa 5 |
| **Sai** | Dicionário v0.3, se nasceu coluna relativa nova | Tarefa 5 |

**Não sai daqui:** outro tipo de modelo, mudança do teste, recálculo do baseline com o Período B.

- [x] O corte é o da Tarefa 2
- [x] Nenhuma coluna de rota entrou

---

## 1. O que o erro pediu

- [x] Citar os erros da Tarefa 3 (classe confundida, caminho longo ou curto, pico isolado virando FALHA, RISCO sumindo)
- [x] Cada mudança da árvore responde a um desses erros
- [x] Parâmetros escolhidos na validação

Diagnóstico da árvore da Tarefa 3 na validação:
- Pares confundidos: só **2 FALHAs previstas como RISCO**.
- Erro por regra do rótulo: regra 3 (`z_robusto` ≥ 3,5) com 2 erros em 3.149 (0,06%); regras 1, 4, 5 e 6 com 0%.
- Erro por escopo (auditoria): 1 em caminho curto (de 5.993), 1 em longo (de 9.982), 0 em regional (de 11.978).
- Pico isolado (OK com aumento > 80%) previsto como FALHA: 0.
- Recall de RISCO 1,000; recall de FALHA 0,999.

**Erro da Tarefa 3 → mudança na árvore:**

| Erro observado | Mudança (profundidade, folha, critério ou métrica relativa nova) | Resultado na validação |
|---|---|---|
| Confusão RISCO ↔ FALHA: 2 FALHAs previstas como RISCO, ambas da regra 3 | Critério **entropia** | ΔF1 macro = 0,0000; mesmas 13 folhas e recall de FALHA 0,9994 |
| Pico isolado virando FALHA: 0 casos; risco de folhas pequenas decorarem o treino | `min_samples_leaf` = 20 | ΔF1 macro = −0,0018; recall de FALHA cai para 0,9922 |
| RISCO sumindo: não aconteceu (recall de RISCO = 1,000; regra 5 com 0% de erro) | Profundidade + 2 (`max_depth` 8) | ΔF1 macro = 0,0000; a profundidade real continua 6 |
| Árvore com 13 folhas, possivelmente maior que o necessário | Poda `ccp_alpha` = 1e-4 e 1e-3 | ΔF1 macro = −0,0004 (10 folhas) e −0,0018 (5 folhas) |
| Erros espalhados em fluxos diferentes (1 curto, 1 longo) | 4 colunas relativas novas: `z_tendencia`, `z_max5`, `n5_jitter3`, `perda_media5` | ΔF1 macro = 0,0000 com os parâmetros da T3 |

Depois dos experimentos isolados, uma **busca combinada de 288 combinações** (critério × profundidade × folha mínima × poda × colunas), escolhida só na validação.

## 2. Árvore ajustada

- [x] Mesmas colunas relativas, mais o que a tabela acima acrescentou
- [x] Profundidade, folhas e três regras em português
- [x] Fit só no treino

**Parâmetros finais candidatos (ainda não é o teste):** CART, critério Gini, `max_depth` 5, `min_samples_leaf` 1, `ccp_alpha` 0,0, semente 42; profundidade obtida 5; **11 folhas**. Colunas: as 8 da Tarefa 3 mais `z_tendencia`, `z_max5`, `n5_jitter3` e `perda_media5`.

**Primeiras divisões:** nível 0 `z_robusto` ≤ 3,501; nível 1 `n5_risco` ≤ 1,5; nível 2 `n5_aumento80` ≤ 1,5 e `jitter_relativo` ≤ 3.

**Regras:**

1. Se `z_robusto` > 3,501 (ou vazio), então **FALHA** (folha com 7.310 medições do treino; 100% delas são FALHA).
2. Se `z_robusto` ≤ 3,501 e `n5_risco` > 1,5 e `jitter_relativo` > 3 (ou vazio) e `perda_pct` ≤ 16,667 e `n5_aumento80` ≤ 1,5, então **RISCO** (folha com 4.640 medições do treino; 100% delas são RISCO).
3. Se `z_robusto` ≤ 3,501 e `n5_risco` ≤ 1,5 e `n5_aumento80` ≤ 1,5 e `perda_pct` ≤ 16,667, então **OK** (folha com 50.325 medições do treino; 100% delas são OK).

## 3. Comparação na validação

| | F1 macro | Recall de FALHA | Recall de RISCO |
|---|---|---|---|
| Árvore da Tarefa 3 | 0,9998 | 0,9994 | 1,000 |
| Árvore desta tarefa | 0,9998 | 0,9994 | 1,000 |

- [x] Se não houve ganho, dizer o que foi tentado e descartado
- [x] Matriz 3×3 da árvore desta tarefa, na validação

| | prev. OK | prev. RISCO | prev. FALHA |
|---|---|---|---|
| **real OK** | 21.912 | 0 | 0 |
| **real RISCO** | 0 | 2.840 | 0 |
| **real FALHA** | 0 | 2 | 3.199 |

Balanced accuracy = 0,9998; acurácia = 0,9999.

**Leitura do ganho (ou da falta de ganho):** nenhuma mudança superou o F1 macro da Tarefa 3, que já estava em 0,9998. Foram tentados e descartados: entropia (sem ganho), folha mínima maior e poda forte (pioraram o recall de FALHA para 0,9922), mais profundidade (sem efeito: a árvore não cresce além de 6). A árvore escolhida, pela regra de desempate, tem o mesmo F1 macro e o mesmo recall de FALHA com **11 folhas em vez de 13**. As colunas novas tornaram isso possível: sem elas, a profundidade 5 chegava só a F1 0,9996 e recall de FALHA 0,9988. O ganho, portanto, é de simplicidade, não de desempenho. O desempenho quase perfeito vem de o rótulo ser feito com as mesmas métricas que a árvore lê.

## 4. Revisão com o docente

**O que foi mostrado:** _(preencher)_  
**O que foi pedido para ajustar antes da Tarefa 5:** _(preencher)_

### Dicionário de dados v0.3

Tudo da v0.2, mais as colunas relativas criadas nesta tarefa (todas usam só medições anteriores ou a atual do mesmo fluxo):

| Coluna | Unidade | Cálculo | Se faltar |
|---|---|---|---|
| `z_tendencia` | — | `z_robusto` atual − média de `z_robusto` nas 3 medições anteriores do fluxo | vazio se o atual ou as 3 anteriores não têm z |
| `z_max5` | — | maior `z_robusto` nas últimas 5 medições (inclui a atual) | vazio se nenhuma das 5 tem z |
| `n5_jitter3` | 0 a 5 | quantas das últimas 5 têm `jitter_relativo` ≥ 3 | — |
| `perda_media5` | % | média de `perda_pct` nas últimas 5 | — |

Continuam proibidos: país, IP, rota, `fluxo_id` e RTT absoluto.

## 5. Scrum e diário

- [X] Board atualizado

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Isaac William Braz | Não atuei diretamente nesta tarefa (responsável: Hendrick). | — | — |
| Fernanda Akemi Martins Sanpei | Não atuei diretamente nesta tarefa (responsável: Hendrick). | — | — |
| Geziel de Andrade | Não atuei diretamente nesta tarefa (responsável: Hendrick). | — | — |
| Hendrick Ambriola | Diagnóstico dos erros da T3; quatro colunas relativas novas; experimentos com uma mudança por vez (entropia, folha mínima, profundidade, poda, colunas novas); busca combinada na validação; tabela T3 → T4; dicionário v0.3. | Ligar cada mudança a um erro, com só 2 erros na validação. Aceitar e documentar que nenhuma mudança trouxe ganho de F1. | Manter a escolha só pela validação. Apresentar ao docente o que foi tentado e descartado. |
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
