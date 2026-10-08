# Diário da Tarefa 3 — Primeira árvore de decisão

**Período:** 28/09/2026 a 04/10/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)

**Equipe:** Grupo 7  
**Scrum Master da tarefa:** Fernanda Akemi Martins Sanpei  
**Repositório GitHub:** https://github.com/GzTop1/Redes-Projeto

> Tarefa 1 coletou. Tarefa 2 fez o baseline e o rótulo. Esta tarefa **não refaz** a ficha nem a tabela de classes.
>
> O modelo é uma **árvore de decisão**. O entregável é a árvore: atributos de cada divisão, profundidade, folhas e as regras lidas em português. Não é um desfile de algoritmos.
>
> A árvore oficial usa só métricas relativas ao baseline do fluxo. Uma segunda árvore, de contraste, pode ver a rota ou o RTT absoluto — só para mostrar que ela aprende distância. Essa árvore de contraste **não** é o modelo do projeto.

### Contrato desta tarefa

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Ficha de baseline, dataset rotulado, corte temporal | Tarefa 2 — **os mesmos** |
| **Sai** | Árvore treinada só no treino, com profundidade e critério registrados | Tarefa 4 mexe nesta árvore, não no rótulo |
| **Sai** | Regras da árvore em texto e matriz 3×3 (OK, RISCO, FALHA) | Tarefa 4, para atacar o erro |
| **Sai** | Árvore de contraste (com rota ou RTT absoluto) e a frase do que ela aprendeu | Prova de que o modelo oficial não segue esse atalho |

**Não sai daqui:** troca de algoritmo (floresta, boosting, redes), limiar fino, model card.

- [x] Treino, validação e teste são os da Tarefa 2 (70.560 / 27.953 / 41.812 medições, conferidos contra `corte_temporal.json`)
- [x] A ficha de baseline não foi recalculada com o Período B (lida de `baseline_por_fluxo.csv`, gravada em 07/10/2026 18:21:42 UTC)

---

## 1. Colunas que a árvore oficial pode usar

Entram: `z_robusto`, `aumento_pct`, `jitter_relativo`, `perda_pct`, `timeout_atual`, `n5_timeout`, `n5_aumento80`, `n5_risco`.

Não entram: país, IP, `rota_id`, `fluxo_id`, nome do destino, RTT em milissegundos no lugar das métricas relativas.

- [x] Lista de colunas do treino colada no diário
- [x] Conferido que a classe (`OK` / `RISCO` / `FALHA`) é o alvo, não uma feature

**Colunas usadas:** `z_robusto`, `aumento_pct`, `jitter_relativo`, `perda_pct`, `timeout_atual`, `n5_timeout`, `n5_aumento80`, `n5_risco`. Alvo: `classe`.

## 2. A árvore

- [x] Uma árvore de decisão (CART, critério **Gini**)
- [x] `max_depth` e `min_samples_leaf` escolhidos olhando **só a validação**, não o teste (grade de profundidade 2 a 10 e folha mínima 1 a 200; maior F1 macro na validação, com desempate por recall de FALHA e depois pela árvore menor)
- [x] Semente registrada: 42
- [x] Ajuste (`fit`) só no treino
- [x] Profundidade real, número de folhas e as primeiras divisões descritas
- [x] Pelo menos três regras no formato “se métrica ≤ limiar e … então classe”, copiadas da árvore

**Critério, profundidade máxima pedida, profundidade obtida, folhas:** Gini; `max_depth` pedido 6; `min_samples_leaf` 1; profundidade obtida 6; 13 folhas; semente 42.

**Primeiras divisões:**
- nível 0: `z_robusto` ≤ 3,501 (70.560 medições do treino)
- nível 1: `n5_risco` ≤ 1,5 (63.250 medições)
- nível 2: `n5_aumento80` ≤ 1,5 (50.351 medições) e `jitter_relativo` ≤ 3 (12.899 medições)

**Regras lidas da árvore:**

1. Se `z_robusto` > 3,501 (ou vazio), então **FALHA** (folha com 7.310 medições do treino; 100% delas são FALHA).
2. Se `z_robusto` ≤ 3,501 e `n5_risco` > 1,5 e `jitter_relativo` > 3 (ou vazio) e `perda_pct` ≤ 16,667 e `n5_aumento80` ≤ 1,5, então **RISCO** (folha com 4.640 medições do treino; 100% delas são RISCO).
3. Se `z_robusto` ≤ 3,501 e `n5_risco` ≤ 1,5 e `n5_aumento80` ≤ 1,5 e `perda_pct` ≤ 16,667, então **OK** (folha com 50.325 medições do treino; 100% delas são OK).

## 3. Leitura do erro

No bloco de **validação**. O teste ficou fechado até a Tarefa 5.

- [x] Matriz 3×3 com contagem
- [x] Precisão, recall e F1 de OK, RISCO e FALHA
- [x] F1 macro
- [x] Acurácia sozinha não decide: com maioria OK, ela fica alta mesmo errando FALHA
- [x] Dois erros concretos: os casos pedidos não apareceram na validação (registrado abaixo)

**Matriz e F1 macro (validação):**

| | prev. OK | prev. RISCO | prev. FALHA |
|---|---|---|---|
| **real OK** | 21.912 | 0 | 0 |
| **real RISCO** | 0 | 2.840 | 0 |
| **real FALHA** | 0 | 2 | 3.199 |

| Classe | Precisão | Recall | F1 | Suporte |
|---|---|---|---|---|
| OK | 1,000 | 1,000 | 1,000 | 21.912 |
| RISCO | 0,999 | 1,000 | 1,000 | 2.840 |
| FALHA | 1,000 | 0,999 | 1,000 | 3.201 |

**F1 macro = 0,9998**; balanced accuracy = 0,9998; acurácia = 0,9999 (não é usada para decidir).

**Erros concretos (fluxo, timestamp, métricas, classe verdadeira, classe da árvore):**
- Caminho longo estável que caiu em FALHA: **o caso não apareceu na validação** (0 medições).
- FALHA de caminho curto que caiu em OK: **o caso não apareceu na validação** (0 medições).
- Os únicos erros foram **2 FALHAs previstas como RISCO**, ambas da regra 3 (`z_robusto` ≥ 3,5), uma em caminho curto e uma em caminho longo. A árvore corta em 3,501, e a regra de rótulo em 3,5.

## 4. Árvore de contraste (não é o modelo)

Treinada no mesmo treino e com os mesmos hiperparâmetros, acrescentando o RTT absoluto (`rtt_ms`) e a rota codificada (`rota_cod`).

- [x] Dizer qual divisão apareceu perto da raiz
- [x] Declarar que essa árvore fica fora da entrega final

| Árvore | Raiz | F1 macro (validação) | Importância de RTT + rota |
|---|---|---|---|
| (a) colunas oficiais + RTT absoluto + rota | `z_robusto` ≤ 3,501 | 0,9998 | 0,0 |
| (b) só RTT absoluto + rota | corte fixo de RTT: `rtt_ms` ≤ 141,2 ms | 0,5571 | 1,0 |

Classe prevista pela árvore (b), por escopo, ao lado da real (validação):

| Escopo | Previsto OK | Real OK | Previsto RISCO | Real RISCO | Previsto FALHA | Real FALHA |
|---|---|---|---|---|---|---|
| curto | 94,7% | 83,2% | 2,2% | 6,7% | 3,1% | 10,0% |
| regional | 95,3% | 80,8% | 3,0% | 9,0% | 1,7% | 10,2% |
| longo | 89,9% | 72,6% | 0,6% | 13,6% | 9,4% | 13,8% |

**O que a árvore de contraste usou na raiz:** um corte fixo de milissegundos (`rtt_ms` ≤ 141,2 ms), que separa os caminhos longos dos demais. Ela aprendeu distância e não degradação: o F1 macro cai para 0,557. Quando as métricas relativas estão disponíveis, a árvore ignora RTT e rota (importância zero). **As duas árvores de contraste ficam fora da entrega final.**

## 5. Scrum e diário

- [X] Board atualizado

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Isaac William Braz | Não atuei diretamente nesta tarefa (responsável: Fernanda). | — | — |
| Fernanda Akemi Martins Sanpei | Árvore CART (Gini) com hiperparâmetros escolhidos só na validação; regras em português lidas da árvore; matriz 3×3, F1 por classe e F1 macro; erros concretos; árvore de contraste com RTT e rota, descartada. | Entender por que a árvore acerta quase tudo: o rótulo usa as mesmas métricas que ela lê. Interpretar pequenas diferenças de limiar (corte em 3,501 contra a regra 3,5). | Manter só colunas relativas e o teste fechado. Levar os erros da validação para a Tarefa 4. |
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
