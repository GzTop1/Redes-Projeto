# Diário da Tarefa 3 — Primeira árvore de decisão

**Período:** 28/09/2026 a 04/10/2026  
**Projeto:** Preditor de degradação de rede relativo ao baseline do fluxo (independente da rota)

**Equipe:** Grupo 7  
**Scrum Master da tarefa:** Fernanda Akemi Martins Sanpei  
**Repositório GitHub:** https://github.com/GzTop1/Redes-Projeto
>
> Tarefa 1 coletou. Tarefa 2 fez o baseline e o rótulo. Esta tarefa **não refaz** a ficha nem a tabela de classes.
>
> O modelo é uma **árvore de decisão**. A árvore oficial usa só variáveis relativas ao baseline do fluxo. A árvore de contraste vê o RTT absoluto e a rota, só para mostrar que aprende distância, e **não** é o modelo do projeto.

### Contrato desta tarefa

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Ficha de baseline, dataset rotulado, corte temporal | Tarefa 2 — **os mesmos** |
| **Sai** | Árvore treinada só no treino (`modelos/arvore_T3.joblib`) | Tarefa 4 |
| **Sai** | Regras da árvore em texto e matriz 3×3 | Tarefa 4, para atacar o erro |
| **Sai** | Árvore de contraste e a frase do que ela aprendeu | Prova de que o modelo oficial não segue esse atalho |

**Não sai daqui:** troca de algoritmo, limiar fino, model card.

- [x] Treino e validação são os da Tarefa 2 (211.040 / 40.651 linhas, lidos de `dataset_final.csv`); o teste continua fechado
- [x] A ficha de baseline não foi recalculada com o Período B (lida de `baseline_por_fluxo.csv`, congelada)

---

## 1. Colunas que a árvore oficial pode usar

**Entram (21):** `perda_pct`, `rtt_ausente`, `razao_rtt_p95`, `razao_rtt_p99`, `razao_jitter_p95`, `amplitude_rtt_rel`, `delta_ttl_clip`, `ttl_reset`, `perda_media_w3`, `rtt_p95_max_w3`, `jitter_p95_max_w3`, `n_rtt_acima_p95_w3`, as mesmas quatro para `w6` e `w12`, e `perdas_consecutivas`.

**Não entram:** país, IP, rota, `id_fluxo`, `anchor_id`, `probe_id`, timestamp, RTT absoluto, TTL bruto, percentis do baseline e a **classe atual**.

- [x] Lista de colunas do treino colada no diário
- [x] Conferido que o alvo é a classe da próxima medição (`alvo`) e que a classe atual não é variável (o notebook faz `assert` contra a lista de colunas proibidas)

## 2. A árvore

- [x] Uma árvore de decisão (CART, critério **Gini**)
- [x] `max_depth` e `min_samples_leaf` escolhidos olhando **só a validação**: grade `max_depth` ∈ {3, 5, 8, 12, None} × `min_samples_leaf` ∈ {1, 20, 100} × `class_weight` ∈ {None, balanced} (30 candidatos); critério de escolha: maior F1 macro na validação, depois menor gap treino−validação, depois a árvore mais rasa
- [x] Semente registrada: 42
- [x] Ajuste (`fit`) só no treino
- [x] Profundidade real, número de folhas e as primeiras divisões descritas
- [x] Três regras no formato "se ... então classe", lidas da árvore

**Critério, profundidade, folhas:** Gini; `max_depth` 12; `min_samples_leaf` 100; `class_weight` None; profundidade obtida 12; **220 folhas**; semente 42. F1 macro de treino menos validação (gap): 0,0233.

**Primeiras divisões:**
- nível 0: `n_rtt_acima_p95_w3` ≤ 2,5 (das últimas 3 medições, quantas ficaram acima do P95)
- nível 1: `perda_media_w3` ≤ 58,33 (lado ≤ 2,5) e `razao_rtt_p99` ≤ 1,00 (lado > 2,5)
- nível 2: `n_rtt_acima_p95_w6` ≤ 1,5, `jitter_p95_max_w3` ≤ −0,50 e `n_rtt_acima_p95_w12` ≤ 11,5

**Regras lidas da árvore (as três folhas com mais amostras de treino):**

1. Se `n_rtt_acima_p95_w3` ≤ 2,5 e `perda_media_w3` ≤ 58,3 e `n_rtt_acima_p95_w6` ≤ 1,5 e `razao_jitter_p95` ≤ 2,02 e `jitter_p95_max_w12` > 0,376 e `perda_media_w12` ≤ 1,39 e `rtt_p95_max_w12` ≤ 1 e `jitter_p95_max_w12` ≤ 48,4 e `jitter_p95_max_w6` ≤ 1,3 e `amplitude_rtt_rel` ≤ 0,0353 e `razao_rtt_p99` > 0,806 e `delta_ttl_clip` > −1,5, então **OK** (65.965 amostras de treino).
2. Mesmo caminho até `amplitude_rtt_rel` ≤ 0,0353, depois `razao_rtt_p99` ≤ 0,806 e `rtt_p95_max_w3` > 0,427, então **OK** (20.723 amostras).
3. Se `n_rtt_acima_p95_w3` ≤ 2,5 e `perda_media_w3` ≤ 58,3 e `n_rtt_acima_p95_w6` ≤ 1,5 e `razao_jitter_p95` ≤ 2,02 e `jitter_p95_max_w12` > 0,376 e `perda_media_w12` ≤ 1,39 e `rtt_p95_max_w12` > 1 e `razao_rtt_p99` ≤ 1 e `n_rtt_acima_p95_w12` ≤ 1,5 e `razao_rtt_p95` ≤ 1 e 0,102 < `razao_jitter_p95` ≤ 0,905, então **OK** (13.175 amostras).

**Leitura:** a raiz pergunta se o fluxo **já está** acima do P95 nas últimas medições. A árvore aprende persistência: se o fluxo está degradado agora, tende a continuar.

## 3. Leitura do erro

No bloco de **validação**. O teste ficou fechado até a Tarefa 5.

- [x] Matriz 3×3 com contagem
- [x] Precisão, recall e F1 de OK, RISCO e FALHA
- [x] F1 macro e comparação com a persistência
- [x] Acurácia sozinha não decide
- [x] Erros concretos

**Matriz (validação). Linha = classe real da próxima medição; coluna = prevista:**

| | prev. OK | prev. RISCO | prev. FALHA |
|---|---|---|---|
| **real OK** | 35.335 | 109 | 86 |
| **real RISCO** | 1.990 | 1.514 | 90 |
| **real FALHA** | 331 | 120 | 1.076 |

| Classe | Precisão | Recall | F1 | Suporte |
|---|---|---|---|---|
| OK | 0,9384 | 0,9945 | 0,9656 | 35.530 |
| RISCO | 0,8686 | 0,4213 | 0,5674 | 3.594 |
| FALHA | 0,8594 | 0,7046 | 0,7744 | 1.527 |

**F1 macro = 0,7691.** Persistência (repetir a classe atual) na mesma validação: **0,7261**.

**Fatias:**

| Fatia | N | F1 macro | Recall FALHA |
|---|---|---|---|
| Transições (a classe muda de t para t+1) | 4.121 | 0,2122 | 0,0049 |
| Início de falha (estava OK/RISCO, a próxima é FALHA) | 406 | 0,0098 | 0,0049 |
| Sem a âncora que concentra as FALHAs | 38.942 | 0,7488 | 0,6252 |

**Erros concretos:** 2.726 erros em 40.651 linhas (6,71%); **87,4% acontecem quando a classe muda** entre t e t+1. A confusão dominante é **RISCO real previsto como OK** (1.990 casos). Exemplo: fluxo `6351_4837` (destino Trípoli/LY), 03/10/2026 19:58:18 UTC: classe atual OK, perda 0%, `razao_rtt_p99` 0,888. A próxima medição foi RISCO, e a árvore previu OK. Nada na medição atual anunciava a mudança.

## 4. Árvore de contraste (não é o modelo)

Treinada no mesmo treino, com a profundidade e a folha mínima da árvore oficial, usando **só** o RTT absoluto (`rtt_ms`, −1 se ausente) e a rota codificada (país da sonda > país da âncora).

- [x] Divisão perto da raiz identificada
- [x] Essa árvore fica fora da entrega final

| Árvore | Raiz | F1 macro (validação) |
|---|---|---|
| Oficial (21 variáveis relativas) | `n_rtt_acima_p95_w3` ≤ 2,5 | 0,7691 |
| Contraste (RTT absoluto + rota) | `rtt_ms` ≤ −0,15 (separa timeouts), depois cortes por código de rota | **0,5279** |
| Persistência | — | 0,7261 |

**O que a árvore de contraste aprendeu:** sem as variáveis relativas, ela separa primeiro os timeouts e depois corta por rota, ou seja, por geografia. O F1 macro cai para 0,5279, abaixo da persistência. **A árvore de contraste fica fora da entrega final.**

## 5. Scrum e diário

- [X] Board atualizado

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Isaac William Braz | Não atuei diretamente nesta tarefa (responsável: Fernanda). | — | — |
| Fernanda Akemi Martins Sanpei | Árvore CART (Gini) com grade e desempate escolhidos só na validação; regras em português lidas da árvore; matriz 3×3, F1 por classe, F1 macro e fatias (transições, início de falha); comparação com a persistência; árvore de contraste com RTT absoluto e rota, descartada. | Entender por que o erro se concentra nas transições: a árvore aprende a manter a classe e quase não antecipa mudanças. | Manter só variáveis relativas e o teste fechado. Levar a confusão RISCO→OK para a Tarefa 4. |
| Geziel de Andrade | Não atuei diretamente nesta tarefa (responsável: Fernanda). | — | — |
| Hendrick Ambriola | Não atuei diretamente nesta tarefa (responsável: Fernanda). | — | — |
| Davi Gabriel Borges dos Santos | Não atuei diretamente nesta tarefa (responsável: Fernanda). | — | — |
| Victor Gabriel Alves | Não atuei diretamente nesta tarefa (responsável: Fernanda). | — | — |

**Link do board:** _https://github.com/users/GzTop1/projects/1_

---

## Rubrica — Tarefa 3 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Árvore oficial | 1,5 | Uma árvore, critério e profundidade declarados, regras em português, fit só no treino | | |
| Métricas de três classes | 1,0 | Matriz 3×3, F1 por classe e F1 macro; acurácia não é o critério | | |
| Independência da rota | 1,0 | Colunas relativas apenas; árvore de contraste mostra o atalho da distância e é descartada | | |
| Scrum + diário | 0,5 | Board e diário de todos | | |
| **Total** | **4,0** | | **___ / 4,0** | |
