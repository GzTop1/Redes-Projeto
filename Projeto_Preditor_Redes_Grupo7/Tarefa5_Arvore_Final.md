# Diário da Tarefa 5 — Árvore final e teste único

**Período:** 12/10/2026 a 25/10/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)

**Equipe:** Grupo 7  
**Scrum Master da tarefa:** Geziel de Andrade  
**Repositório GitHub:** https://github.com/GzTop1/Redes-Projeto

> A árvore que entra aqui é a da Tarefa 4. O baseline e o rótulo são os da Tarefa 2. O teste, guardado desde a Tarefa 2, é medido **uma vez**.
>
> Continua sendo uma árvore de decisão. O grupo entrega as regras, a matriz e o que a árvore faz num fluxo que ela não viu — desde que esse fluxo tenha a própria ficha de baseline, calculada só no período inicial dele.

### Contrato desta tarefa

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Corte da Tarefa 2 e ficha de baseline | Tarefa 2 |
| **Entra** | Árvore ajustada e regras | Tarefa 4 |
| **Sai** | Teste único: matriz 3×3, F1 por classe, F1 macro | Entrega |
| **Sai** | Checagem de fluxo não visto, com baseline próprio | Entrega |
| **Sai** | Ficha da árvore (abaixo) e dicionário v0.4 igual às colunas usadas | Entrega |

Não há tarefa seguinte.

- [x] A profundidade não foi escolhida de novo olhando o teste (árvore congelada em `config/arvore_final.json` antes da abertura)
- [x] O baseline do teste não usou medição do próprio teste (ficha só do Período A)

---

## 1. Árvore que será medida

- [x] Critério, profundidade, mínimo de amostras na folha, colunas
- [x] Três regras em português, as mesmas da Tarefa 4
- [x] Confirmação de que país, IP, rota e RTT absoluto não estão na árvore

**Parâmetros:** CART, critério Gini, `max_depth` 5, `min_samples_leaf` 1, `ccp_alpha` 0,0, semente 42; profundidade 5; 11 folhas.  
**Colunas:** `z_robusto`, `aumento_pct`, `jitter_relativo`, `perda_pct`, `timeout_atual`, `n5_timeout`, `n5_aumento80`, `n5_risco`, `z_tendencia`, `z_max5`, `n5_jitter3`, `perda_media5`. País, IP, rota e RTT absoluto na árvore: **não**.  
**Regras:**

1. Se `z_robusto` > 3,501 (ou vazio), então **FALHA** (folha com 7.310 medições do treino; 100% delas são FALHA).
2. Se `z_robusto` ≤ 3,501 e `n5_risco` > 1,5 e `jitter_relativo` > 3 (ou vazio) e `perda_pct` ≤ 16,667 e `n5_aumento80` ≤ 1,5, então **RISCO** (folha com 4.640 medições do treino; 100% delas são RISCO).
3. Se `z_robusto` ≤ 3,501 e `n5_risco` ≤ 1,5 e `n5_aumento80` ≤ 1,5 e `perda_pct` ≤ 16,667, então **OK** (folha com 50.325 medições do treino; 100% delas são OK).

## 2. Teste temporal (uma vez)

Fluxos conhecidos, período mais recente do Período B (18/09/2026 02:08 a 20/09/2026 04:32 UTC, 41.812 medições). Teste aberto em 07/10/2026 18:25:26 UTC (`data/processed/teste_unico.json`).

- [x] Matriz 3×3 com contagem, não só porcentagem
- [x] Precisão, recall e F1 de OK, RISCO e FALHA
- [x] F1 macro
- [x] Recall de FALHA e a troca RISCO ↔ FALHA comentados
- [x] Dois casos: um acerto em caminho longo estável (classe OK) e um erro relevante

**Matriz:**

| | prev. OK | prev. RISCO | prev. FALHA |
|---|---|---|---|
| **real OK** | 33.159 | 0 | 0 |
| **real RISCO** | 0 | 4.996 | 0 |
| **real FALHA** | 2 | 2 | 3.653 |

| Classe | Precisão | Recall | F1 | Suporte |
|---|---|---|---|---|
| OK | 1,000 | 1,000 | 1,000 | 33.159 |
| RISCO | 1,000 | 1,000 | 1,000 | 4.996 |
| FALHA | 1,000 | 0,999 | 0,999 | 3.657 |

**F1 macro no teste:** **0,9997** (balanced accuracy 0,9996; acurácia 0,9999). A regra "sempre OK" (classe majoritária) teria F1 macro de 0,2949, balanced accuracy de 0,3333 e recall de FALHA zero.

**Recall de FALHA e troca RISCO ↔ FALHA:** recall de FALHA de 0,9989. Das 3.657 FALHAs reais, 2 foram previstas como RISCO e 2 como OK. Nenhum RISCO real foi previsto como FALHA, e nenhum OK virou alerta.

**Casos:**
- **Acerto em caminho longo (OK):** fluxo `6410|103.202.216.76` (BR→JP), 19/09/2026 12:07:16 UTC. RTT de 300,6 ms, `z_robusto` 2,49, aumento de 4,9%, perda 0%, `n5_risco` 1. Classe real OK, prevista OK: um RTT de 300 ms dentro do normal do fluxo não virou alerta.
- **Erro relevante (FALHA prevista como OK):** fluxo `6349|103.202.216.76` (BR→JP), 19/09/2026 03:03:05 UTC. Perda de 33,3% (1 pacote em 3), `z_robusto` 1,62, `n5_risco` 4. A classe real é FALHA pela regra 1 (perda ≥ 10%), mas a árvore previu OK: a medição caiu num ramo que não testa `perda_pct`. Perda isolada é rara no treino (236 medições no Período B inteiro).

## 3. Fluxo que a árvore não viu

Fluxos separados na Tarefa 2, **antes** de qualquer árvore. A ficha de cada um vem só do Período A (até 13/09/2026 04:30 UTC), e a avaliação usa o Período B inteiro deles.

- [x] O fluxo novo não aparece no treino
- [x] A mediana e o MAD não usam o trecho avaliado
- [x] Dizer se um caminho longo estável permaneceu OK e se uma degradação foi marcada RISCO ou FALHA
- [x] Havia fluxos com baseline suficiente (todos com pelo menos 2.499 RTT válidos, acima do piso de 1.500)

**Fluxos separados:**

| `fluxo_id` | Rota (auditoria) | RTT válidos no A | Mediana (ms) | MAD (ms) |
|---|---|---|---|---|
| `6349\|43.228.174.199` | BR→JP (longo) | 2.499 | 296,558 | 1,550 |
| `6410\|43.228.174.199` | BR→JP (longo) | 2.509 | 305,813 | 3,567 |
| `6659\|43.228.174.199` | BR→JP (longo) | 2.511 | 271,639 | 0,331 |
| `6891\|43.228.174.199` | BR→JP (longo) | 2.502 | 271,985 | 1,815 |
| `6410\|200.132.1.32` | BR→BR (curto) | 2.511 | 16,522 | 0,540 |
| `6659\|200.132.1.32` | BR→BR (curto) | 2.520 | 15,719 | 0,448 |
| `6891\|200.132.1.32` | BR→BR (curto) | 2.518 | 23,284 | 0,671 |
| `7019\|200.132.1.32` | BR→BR (curto) | 2.519 | 11,872 | 0,064 |

**Resultado:** 20.108 medições; matriz [[17.488, 1, 0], [0, 1.264, 0], [1, 0, 1.354]]; **F1 macro 0,9997**.
- **Caminho longo estável:** 100% das medições OK dos fluxos BR→JP continuaram OK.
- **Degradação em caminho curto:** 100% das 1.117 medições RISCO/FALHA reais dos fluxos BR→BR foram marcadas como RISCO ou FALHA.
- Em todos os fluxos não vistos: 2.619 degradações reais, das quais 2.618 marcadas como RISCO ou FALHA (uma FALHA prevista como OK).

## 4. O que declarar

- [x] **A árvore repete a tabela de rótulo.** Ela concorda com a tabela em 99,99% das medições do teste. O rótulo foi feito com as mesmas métricas que ela lê, então a árvore aprendeu a **política** da Tarefa 2, não um ticket de roteador.
- [x] **Detector ou preditor.** Alvo: classe da medição do mesmo fluxo mais próxima de t + 12 min (tolerância de ±2 min, no mesmo bloco). No teste (41.352 medições com alvo futuro), com os mesmos parâmetros da árvore final:

  | | F1 macro | Recall FALHA | Recall RISCO |
  |---|---|---|---|
  | Árvore (+12 min) | 0,5149 | 0,2520 | 0,1592 |
  | Repetir a classe atual | 0,5409 | 0,4004 | 0,3554 |

  Sem ganho sobre a persistência (−0,026 de F1 macro): **o entregável é um detector do estado atual, não um preditor.**
- [x] **Limitações:**
  - O baseline é fixo (Período A) e não acompanha troca de rota; o estado RECALIBRAR não foi implementado.
  - A rajada de 3 pacotes estima mal o jitter, e uma única perda já dá 33%.
  - As Anchors do RIPE Atlas ficam em data centers e não são a rede do campus.
  - O MAD é de fração de milissegundo (0,08 ms nos curtos, 0,87 ms nos longos), e 98% das FALHAs vêm da regra 3. O rótulo mede sensibilidade estatística, não necessariamente degradação percebida.
  - Timeout persistente não apareceu (regra 2 com 0 casos), então a árvore não foi testada nesse caso.
  - Os fluxos não são independentes (os mesmos probes servem vários destinos) e há 399 lacunas na coleta.

## 5. Ficha da árvore

| Campo | Conteúdo |
|---|---|
| Problema | Classe OK, RISCO ou FALHA pelo desvio ao baseline do fluxo |
| Unidade | Uma medição de um `fluxo_id` no Período B |
| Baseline | Período A (06/09 a 13/09/2026), mediana e MAD, piso de 1.500 RTT válidos |
| Colunas | `z_robusto`, `aumento_pct`, `jitter_relativo`, `perda_pct`, `timeout_atual`, `n5_timeout`, `n5_aumento80`, `n5_risco`, `z_tendencia`, `z_max5`, `n5_jitter3`, `perda_media5` |
| Árvore | CART, critério Gini, `max_depth` 5, profundidade real 5, 11 folhas, `min_samples_leaf` 1, `ccp_alpha` 0,0, semente 42 |
| Teste (uma vez) | F1 macro 0,9997 (classe majoritária: 0,2949); balanced accuracy 0,9996; recall de FALHA 0,999 |
| Fluxo não visto | BR→JP e BR→BR: F1 macro 0,9997; longo estável 100% OK; curto degradado 100% RISCO/FALHA |
| Detector ou preditor | Detector: o preditor de 12 min não supera "repetir a classe atual" (0,5149 contra 0,5409) |
| O que ela não faz | Não classifica distância. Não opera em fluxo sem ficha. |
| Como reproduzir | `requirements.txt` (pandas 2.2.3, numpy 2.1.3, requests 2.32.4, scikit-learn 1.6.1, matplotlib 3.10.0, joblib 1.6.0), notebook `Projeto_Preditor_Falhas_PPF_.ipynb` executado de cima para baixo, `config/` (`parametros.json`, `tabela_desenho.csv`, `corte_temporal.json`, `arvore_final.json`) |

**Dicionário v0.4:** igual às 12 colunas acima, mais `classe` (alvo). Fora da árvore: país, IP, rota, escopo, `fluxo_id`, timestamp e RTT absoluto (notebook, seção 5.5).

## 6. Scrum e diário

- [X] Board atualizado

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Isaac William Braz | Não atuei diretamente nesta tarefa (responsável: Geziel). | — | — |
| Fernanda Akemi Martins Sanpei | Não atuei diretamente nesta tarefa (responsável: Geziel). | — | — |
| Geziel de Andrade | Árvore congelada antes do teste; teste único (matriz, F1, balanced accuracy, comparação com a classe majoritária); fluxos não vistos BR→JP e BR→BR; preditor de 12 min × persistência; limitações; ficha da árvore e dicionário v0.4. | Abrir o teste uma única vez, sem ajustar nada depois. Interpretar o preditor contra "repetir a classe atual" e concluir que o entregável é um detector. | Declarar as limitações com clareza (baseline fixo, rajada de 3 pacotes, Anchors ≠ rede do campus). Manter a ficha alinhada às colunas usadas. |
| Hendrick Ambriola | Não atuei diretamente nesta tarefa (responsável: Geziel). | — | — |
| Davi Gabriel Borges dos Santos | Não atuei diretamente nesta tarefa (responsável: Geziel). | — | — |
| Victor Gabriel Alves | Não atuei diretamente nesta tarefa (responsável: Geziel). | — | — |

**Link do board:** _https://github.com/users/GzTop1/projects/1_

---

## Rubrica — Tarefa 5 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Árvore final legível | 1,0 | Regras em português, colunas relativas, parâmetros da Tarefa 4 | | |
| Teste único | 1,5 | Matriz 3×3 em contagem, F1 por classe, F1 macro, casos curto/longo; teste não escolheu a árvore | | |
| Fluxo novo com baseline próprio | 1,0 | Ficha só no período inicial; ou limitação declarada se faltou fluxo | | |
| Ficha + diário | 0,5 | Ficha preenchida e diário de todos | | |
| **Total** | **4,0** | | **___ / 4,0** | |
ss