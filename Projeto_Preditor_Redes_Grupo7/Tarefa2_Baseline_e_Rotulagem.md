# Diário da Tarefa 2 — Baseline do fluxo e rotulagem OK, RISCO, FALHA

**Período:** 18/09/2026 a 30/09/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)

**Equipe:** Grupo 7  
**Scrum Master da tarefa:** Davi Gabriel Borges dos Santos  
**Repositório GitHub:** https://github.com/GzTop1/Redes-Projeto

> Esta tarefa lê o `data/raw/` da Tarefa 1. Não troca a coleta sem versionar.
>
> O trabalho é **obter o baseline de cada fluxo e rotular o Período B** com a tabela desta página. A árvore não entra aqui. País, IP e rota não entram na tabela que a árvore vai ler.
>
> Ordem obrigatória: inspeção do bruto → ficha de baseline no Período A → métricas relativas no Período B → rótulo na ordem da tabela → só então o recorte temporal dentro de B.

### Contrato desta tarefa

|           | Artefato                                                              | Origem / destino                            |
| --------- | --------------------------------------------------------------------- | ------------------------------------------- |
| **Entra** | `data/raw/` e dicionário v0.1                                         | Tarefa 1                                    |
| **Sai**   | `baseline_por_fluxo.csv` (uma ficha por `fluxo_id`)                   | Tarefas 3 a 5                               |
| **Sai**   | Dataset rotulado do Período B, com a classe e as métricas abaixo      | Tarefa 3 **usa este arquivo e este rótulo** |
| **Sai**   | Recorte temporal dentro de B (treino mais antigo, teste mais recente) | Tarefas 3 a 5 — **o mesmo corte**           |
| **Sai**   | Dicionário v0.2 (bruto, ficha, métricas, classe, colunas proibidas)   | Tarefa 3                                    |

**Não sai daqui:** árvore treinada, profundidade escolhida, acurácia, F1.

- [x] O notebook lê o bruto da Tarefa 1 (seção 2.1 relê os 224 JSON de `data/raw/` e confere contra `bruto_tabela.csv`)

---

## 1. Inspeção do bruto (ainda sem rótulo)

`data/raw/` permanece intocado. A auditoria vai para o diário; a tabela de trabalho, para `data/interim/`.

- [x] Contagem de linhas, fluxos, duplicatas e RTT vazio
- [x] Nenhum RTT ausente foi gravado como 0
- [x] Período A e Período B não compartilham timestamp do mesmo fluxo

| Conferência | Relido de `data/raw/` | `bruto_tabela.csv` (Tarefa 1) |
|---|---|---|
| Registros | 322.016 | 322.016 |
| Fluxos | 64 | 64 |
| Timeouts | 227 | 227 |
| RTT vazio | 227 | 227 |

**N bruto:** 322.016 registros (161.135 no Período A e 160.881 no B), lidos de 224 arquivos; 42 arquivos dos destinos descartados foram ignorados.  
**N de fluxos:** 64  
**Evidências:** duplicatas 0; linhas sem `sent` 0; RTT = 0: 0; timestamps (fluxo, instante) presentes em A e em B ao mesmo tempo: 0. Notebook, seção 2.1; print `T2_2.1_inspecao_bruto.png`.

## 2. Como obter o baseline

Uma ficha por `fluxo_id`. Só o Período A. O Período B não entra na conta e não atualiza a ficha.

| Passo | O que fazer                                                                                                            |
| ----- | ---------------------------------------------------------------------------------------------------------------------- |
| 1     | Separar o fluxo e ordenar pelo timestamp.                                                                              |
| 2     | Período A = bloco inicial. Período B = bloco seguinte, sem amostra nos dois.                                           |
| 3     | RTT válido = medição com RTT presente. Timeout fica **fora** da mediana e do MAD, e **dentro** do dataset como evento. |
| 4     | Menos de **1.500** RTT válidos no A: `baseline_insuficiente`. Esse fluxo **não** recebe classe. Não inventar mediana.  |
| 5     | Gravar uma linha em `baseline_por_fluxo.csv` e congelar.                                                               |

| Campo da ficha  | Fórmula, somente Período A                                 |
| --------------- | ---------------------------------------------------------- |
| `mediana`       | mediana dos RTT válidos (ms)                               |
| `MAD`           | mediana(\|RTT − mediana\|) dos RTT válidos (ms)            |
| `jitter_tipico` | mediana do jitter nas medições em que o jitter existe (ms) |
| `perda_tipica`  | mediana de `perda_pct`, inclusive timeout (%)              |
| `prop_resposta` | medições com RTT válido / medições do período              |

A ficha também guarda `IQR` (usado só quando MAD = 0), `n_medicoes_A`, `n_rtt_validos_A`, `inicio_A` e `fim_A`. Ela é congelada: uma nova execução recalcula e exige resultado idêntico ao gravado.

- [x] Ficha conferida em pelo menos um fluxo curto e um fluxo longo (recalculada com numpy direto dos RTT do Período A)
- [x] Lista dos fluxos excluídos e o motivo (nenhum fluxo abaixo de 1.500)

**Fluxos com ficha:** 64  
**Fluxos excluídos:** nenhum. Todos os 64 fluxos têm mais de 1.500 RTT válidos no Período A.  
**Exemplo auditável (fluxo curto: mediana; fluxo longo: mediana):**
- Curto `6372|217.198.242.227` (DE→DE, Mainz): 2.519 RTT válidos; mediana **9,88 ms**; MAD 0,09 ms; jitter típico 0,10 ms; perda típica 0%; proporção de resposta 1,0000.
- Longo `6410|217.198.242.227` (BR→DE, Mainz): 2.513 RTT válidos; mediana **208,50 ms**; MAD 2,18 ms; jitter típico 0,10 ms; perda típica 0%; proporção de resposta 0,9996.

As duas medianas são muito diferentes, e as duas são o "normal" do próprio fluxo. Mediana da ficha por escopo (só auditoria): curto 9,63 ms (MAD 0,08), regional 36,29 ms (MAD 0,20), longo 203,91 ms (MAD 0,87).

## 3. Métricas de cada medição do Período B

Calcular só com a ficha congelada daquele `fluxo_id`.

| Métrica           | Fórmula                                                                 |
| ----------------- | ----------------------------------------------------------------------- |
| `z_robusto`       | (RTT atual − mediana) / (1,4826 × MAD)                                  |
| `aumento_pct`     | (RTT atual − mediana) / mediana × 100                                   |
| `jitter_relativo` | jitter atual / `jitter_tipico`                                          |
| `perda_pct`       | (enviados − recebidos) / enviados × 100                                 |
| `timeout_atual`   | 1 se não há RTT ou `perda_pct` = 100; senão 0                           |
| `n5_timeout`      | timeouts nas últimas 5 medições deste fluxo, incluindo a atual (0 a 5)  |
| `n5_aumento80`    | quantas das últimas 5 têm `aumento_pct` > 80                            |
| `n5_risco`        | quantas das últimas 5 cumprem o critério da linha 5 da tabela de rótulo |

| Situação                               | Conta                                                                           |
| -------------------------------------- | ------------------------------------------------------------------------------- |
| RTT ausente                            | Não calcular `z_robusto` nem `aumento_pct`. `timeout_atual` = 1. Não usar 0 ms. |
| MAD = 0 e RTT atual = mediana          | `z_robusto` = 0                                                                 |
| MAD = 0 e RTT atual ≠ mediana          | Denominador = max(IQR / 1,349, 1 ms)                                            |
| Jitter atual vazio                     | O critério de jitter não dispara                                                |
| `jitter_tipico` = 0 e jitter atual = 0 | `jitter_relativo` = 1                                                           |
| `jitter_tipico` = 0 e jitter atual > 0 | Tratar como `jitter_relativo` ≥ 3                                               |

**Resultado:** 160.881 medições do Período B em 64 fluxos. Casos especiais: MAD = 0 em 0 linhas e `jitter_tipico` = 0 em 0 linhas. `z_robusto` e `aumento_pct` ficam vazios nas 55 medições sem RTT do Período B; `jitter_relativo` fica vazio em 159. Há 399 intervalos maiores que 360 s entre medições seguidas do mesmo fluxo. As janelas de 5 contam só medições do Período B.

## 4. Tabela de rotulagem — parar na primeira linha verdadeira

Cada linha do Período B, de um fluxo que tenha ficha. FALHA ganha de RISCO; RISCO ganha de OK.

| Ordem | Classe    | Métrica                                                                                                   | Limiar exato                                        | Medições |
| ----- | --------- | --------------------------------------------------------------------------------------------------------- | --------------------------------------------------- | --- |
| 1     | **FALHA** | `perda_pct`                                                                                               | ≥ 10 nesta medição (em 3 pacotes, 1 perda já é 33%) | 236 |
| 2     | **FALHA** | `n5_timeout`                                                                                              | ≥ 3                                                 | 0 |
| 3     | **FALHA** | `z_robusto`                                                                                               | ≥ 3,5 nesta medição, com RTT presente               | 15.305 |
| 4     | **FALHA** | `n5_aumento80`                                                                                            | ≥ 2                                                 | 60 |
| 5     | **RISCO** | nesta medição, pelo menos um: `2 ≤ z_robusto < 3,5`, ou `30 ≤ aumento_pct ≤ 80`, ou `jitter_relativo ≥ 3` | e `n5_risco` ≥ 2                                    | 15.249 |
| 6     | **OK**    | nenhuma linha anterior                                                                                    | pico isolado também é OK                            | 130.031 |

- [x] Três exemplos auditáveis no diário: um OK de caminho longo (RTT alto e `z_robusto` baixo), um RISCO, um FALHA de caminho curto
- [x] Contagem OK / RISCO / FALHA no Período B
- [x] A classe **não** foi definida por “RTT > 100 ms” nem pelo nome da rota: das 70.342 medições com RTT > 100 ms, 77,4% são OK
- [x] O Período A não foi rotulado
- [x] Dicionário v0.2 lista as colunas proibidas na árvore: país, cidade, IP/`dst_addr`, `prb_id`, `msm_id`, rota, escopo, `fluxo_id`, timestamp e RTT absoluto (`rtt_ms`, `min`, `max`, `jitter_ms`); `regra` e `risco_atual` também ficam fora

**Contagem OK / RISCO / FALHA:** 130.031 / 15.249 / 15.601 (80,82% / 9,48% / 9,70%)

| Escopo (só auditoria) | OK | RISCO | FALHA |
|---|---|---|---|
| curto | 85,30% | 6,56% | 8,15% |
| regional | 82,01% | 9,07% | 8,92% |
| longo | 76,65% | 11,84% | 11,51% |

**Evidências (três linhas reais, com as métricas e a ordem que disparou a classe):**

| | OK de caminho longo | RISCO | FALHA de caminho curto |
|---|---|---|---|
| `fluxo_id` | `6410\|43.228.174.199` | `6410\|104.225.3.74` | `6313\|217.198.242.227` |
| Rota (auditoria) | BR→JP | BR→US | DE→DE |
| Timestamp (UTC) | 19/09/2026 13:29:50 | 17/09/2026 10:52:00 | 13/09/2026 04:35:17 |
| RTT (ms) | 311,10 | 143,20 | 2,17 |
| `z_robusto` | 1,00 | 0,53 | 6,38 |
| `aumento_pct` | 1,73 | 1,48 | 45,06 |
| `jitter_relativo` | 0,73 | 4,89 | 11,10 |
| `perda_pct` | 0 | 0 | 0 |
| `n5_timeout` / `n5_aumento80` / `n5_risco` | 0 / 0 / 0 | 0 / 0 / 2 | 0 / 0 / 1 |
| Regra que disparou | 6 (OK) | 5 (jitter relativo ≥ 3 e `n5_risco` ≥ 2) | 3 (`z_robusto` ≥ 3,5) |
| Classe | OK | RISCO | FALHA |

## 5. Recorte para a árvore (ainda sem treinar)

Dentro do Período B, por fluxo, em ordem de tempo:

- [x] Treino = trecho mais antigo; validação = trecho do meio; teste = trecho mais recente
- [x] Proporção de partida 50% / 20% / 30% (todos os blocos ficaram com RISCO, sem ajuste)
- [x] Nenhum registro do Período A no treino
- [x] Corte com data e N de cada bloco

Duas decisões tomadas aqui, antes de qualquer árvore:
- **Folga entre blocos (RFC §9):** as 4 primeiras medições de cada fluxo no início da validação e do teste ficam fora dos blocos, para nenhuma janela de 5 usar medições do bloco anterior.
- **Fluxos não vistos (para a Tarefa 5):** todos os fluxos para Tsuchiura (BR→JP, longo) e Porto Alegre (BR→BR, curto) ficam fora de treino, validação e teste: `6349|43.228.174.199`, `6410|43.228.174.199`, `6659|43.228.174.199`, `6891|43.228.174.199`, `6410|200.132.1.32`, `6659|200.132.1.32`, `6891|200.132.1.32` e `7019|200.132.1.32`.

Uma primeira versão do corte (sem folga e com Detroit e Apeldoorn como não vistos) foi versionada em `versao_anterior_corte_v1/` e substituída por esta, para cumprir o RFC.

**Corte (datas e N treino / validação / teste):**

| Bloco | De (UTC) | Até (exclusivo) | OK | RISCO | FALHA | N |
|---|---|---|---|---|---|---|
| Treino | 13/09/2026 04:32 | 16/09/2026 16:32 | 57.089 | 6.106 | 7.365 | **70.560** |
| Validação | 16/09/2026 16:32 | 18/09/2026 02:08 | 21.912 | 2.840 | 3.201 | **27.953** |
| Teste | 18/09/2026 02:08 | 20/09/2026 04:32 | 33.159 | 4.996 | 3.657 | **41.812** |
| Não vistos | 13/09/2026 04:32 | 20/09/2026 04:32 | 17.489 | 1.264 | 1.355 | 20.108 |
| Folga | — | — | 382 | 43 | 23 | 448 |

Proporção por fluxo (mínimo / máximo): treino 0,502 / 0,507; validação 0,198 / 0,201; teste 0,292 / 0,300. Arquivos gravados: `data/processed/periodo_B_rotulado.csv` e `config/corte_temporal.json`.

## 6. Scrum e diário

- [X] Board atualizado

**Link do board:** _https://github.com/users/GzTop1/projects/1_

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
| ---------- | ---------------------- | ------------ | ----------------------------- |
| Isaac William Braz | Não atuei diretamente nesta tarefa (responsável: Davi). | — | — |
| Fernanda Akemi Martins Sanpei | Não atuei diretamente nesta tarefa (responsável: Davi). | — | — |
| Geziel de Andrade | Não atuei diretamente nesta tarefa (responsável: Davi). | — | — |
| Hendrick Ambriola | Não atuei diretamente nesta tarefa (responsável: Davi). | — | — |
| Davi Gabriel Borges dos Santos | Inspeção do bruto; ficha de baseline só com o Período A (piso de 1.500) e conferência com numpy; métricas relativas do Período B; rótulo na ordem da tabela; recorte 50/20/30 com folga e fluxos não vistos; dicionário v0.2. | Aplicar os casos especiais (MAD = 0, jitter típico = 0, RTT ausente). O MAD de vários fluxos é menor que 1 ms, o que deixa o z robusto muito sensível. A trava do notebook bloqueou o corte novo, e foi preciso versionar o corte antigo. | Manter a ficha congelada e o corte único para as Tarefas 3 a 5. Registrar no diário qualquer mudança de corte, com o motivo. |
| Victor Gabriel Alves | Não atuei diretamente nesta tarefa (responsável: Davi). | — | — |

---

## Rubrica — Tarefa 2 (0 a 4,0)

| Critério                  | Peso    | Nota máxima                                                                                     | Nota          | Observações |
| ------------------------- | ------- | ----------------------------------------------------------------------------------------------- | ------------- | ----------- |
| Baseline por fluxo        | 1,5     | Ficha só com o Período A, fórmulas desta página, piso de 1.500, exclusões listadas, A congelado |               |             |
| Rotulagem                 | 1,5     | Tabela aplicada na ordem, exemplos curto/longo, timeout sem RTT = 0, contagem das três classes  |               |             |
| Independência da rota     | 0,5     | Rota e RTT absoluto fora do rótulo e fora das colunas da futura árvore                          |               |             |
| Recorte temporal + diário | 0,5     | Corte dentro de B, com N; diário de todos                                                       |               |             |
| **Total**                 | **4,0** |                                                                                                 | **___ / 4,0** |             |
