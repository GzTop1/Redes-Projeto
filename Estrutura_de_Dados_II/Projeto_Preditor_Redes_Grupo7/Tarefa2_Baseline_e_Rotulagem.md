# Diário da Tarefa 2 — Baseline do fluxo e rotulagem OK, RISCO, FALHA

**Período:** 18/09/2026 a 30/09/2026  
**Projeto:** Preditor de degradação de rede relativo ao baseline do fluxo (independente da rota)

**Equipe:** Grupo 7  
**Scrum Master da tarefa:** Davi Gabriel Borges dos Santos  
**Repositório GitHub:** https://github.com/GzTop1/Redes-Projeto

> Esta tarefa lê o `data/raw/` da Tarefa 1. O trabalho é **obter o baseline de cada fluxo e rotular o Período B** com a tabela desta página. A árvore não entra aqui. País, IP e rota não entram na tabela que o modelo vai ler.
>
> Ordem obrigatória: inspeção do bruto → ficha de baseline no Período A → métricas relativas no Período B → rótulo na ordem da tabela → só então o recorte temporal dentro de B.

### Contrato desta tarefa

|           | Artefato                                                              | Origem / destino                            |
| --------- | --------------------------------------------------------------------- | ------------------------------------------- |
| **Entra** | `data/raw/` e dicionário v0.1                                         | Tarefa 1                                    |
| **Sai**   | `baseline_por_fluxo.csv` (uma ficha por `id_fluxo`)                   | Tarefas 3 a 5                               |
| **Sai**   | Dataset rotulado do Período B (`dataset_final.csv`)                   | Tarefa 3 **usa este arquivo e este rótulo** |
| **Sai**   | Recorte temporal dentro de B (`corte_temporal.json`)                  | Tarefas 3 a 5 — **o mesmo corte**           |
| **Sai**   | Dicionário v0.2                                                       | Tarefa 3                                    |

**Não sai daqui:** árvore treinada, profundidade escolhida, acurácia, F1.

- [x] O notebook lê o bruto da Tarefa 1 (seção 2.1 relê os 420 JSON de `data/raw/` e confere contra `bruto_tabela.csv`)

---

## 1. Inspeção do bruto (ainda sem rótulo)

- [x] Contagem de linhas, fluxos, duplicatas e RTT vazio
- [x] Nenhum RTT ausente foi gravado como 0
- [x] Período A e Período B não compartilham timestamp

| Conferência | Relido de `data/raw/` | `bruto_tabela.csv` (Tarefa 1) |
|---|---|---|
| Registros | 695.132 | 695.132 |
| Soma do RTT médio | idêntica | idêntica |
| RTT gravado como 0 | 0 | 0 |

**N bruto:** 695.132 registros (345.094 no Período A e 350.038 no B), de 420 arquivos.  
**N de fluxos com resultado:** 141 (dos 150 desenhados). Seguem para esta tarefa os **131 fluxos A+B** da Tarefa 1.  
**Evidências:** duplicatas 0; RTT = 0: 0; último timestamp do A em 28/09/2026 17:59:53 UTC e primeiro do B em 28/09/2026 18:00:13 UTC; TTL presente em 95,5% das linhas; RTT ausente (timeout) em 4,51%. Notebook, seção 2.1.

## 2. Como obter o baseline

Uma ficha por `id_fluxo`, só com o Período A. O Período B não entra na conta.

| Passo | O que foi feito |
| ----- | --------------- |
| 1     | Separar o fluxo e ordenar pelo timestamp. |
| 2     | Período A = 21/09 18:00 a 28/09 18:00 UTC; Período B = até 05/10 18:00 UTC. |
| 3     | RTT válido = RTT presente. Timeout fica fora dos percentis e dentro do dataset como evento. |
| 4     | Menos de **30** RTT válidos no A: `status_baseline = INSUFICIENTE`, sem classe. |
| 5     | Gravar `baseline_por_fluxo.csv` e congelar (uma nova execução exige resultado idêntico). |

**Mínimo de 30 RTT válidos em vez do piso de 1.500.** A rubrica desta tarefa cita um piso de 1.500 RTT válidos, mas o grupo adotou o mínimo de **30**, que é o valor do pipeline de referência da professora (`pipeline/06_baseline/src/config.py`: `MIN_AMOSTRAS_BASELINE = 30`; percentis `(95, 99)`). A troca acompanha a mudança do baseline de mediana/MAD para P95/P99 (correção C09 do notebook). O piso de 1.500 também fica coberto na prática pela regra de cobertura da Tarefa 1: um fluxo só chega aqui com pelo menos 2.016 execuções no Período A (80% de 2.520). A contagem de RTT válidos de cada fluxo está na coluna `n_rtt_validos_A` de `baseline_por_fluxo.csv`.

| Campo da ficha  | Fórmula, somente Período A |
| --------------- | -------------------------- |
| `mediana_rtt_A` | mediana do RTT médio válido (ms) |
| `p95_rtt_A`, `p99_rtt_A` | percentis 95 e 99 do RTT médio (interpolação linear) |
| `mediana_jitter_A`, `p95_jitter_A`, `p99_jitter_A` | mediana e percentis do jitter populacional |
| `ttl_baseline` | mediana do TTL |
| `n_amostras_A`, `n_rtt_validos_A`, `status_baseline` | contagens e status |

- [x] Ficha conferida em um fluxo curto e um longo (percentil recalculado com interpolação feita à mão)
- [x] Lista dos fluxos excluídos e o motivo

**Fluxos com ficha VÁLIDA:** 131 de 131.  
**Fluxos excluídos nesta tarefa:** nenhum. Os 19 fluxos sem cobertura já tinham saído na Tarefa 1 (`config/exclusoes_fluxos.csv`).  
**Exemplo auditável:**
- Curto `7326_1526` (destino Sydney/AU): mediana **0,80 ms**; P95 0,91; P99 1,05.
- Longo `6506_2581` (destino Dubai/AE): mediana **451,57 ms**; P95 489,87; P99 656,78.

As duas medianas são muito diferentes, e as duas são o "normal" do próprio fluxo.

## 3. Métricas de cada medição do Período B

Calculadas só com a ficha congelada daquele `id_fluxo`.

| Métrica | Fórmula |
| ------- | ------- |
| `razao_rtt_p95`, `razao_rtt_p99` | RTT atual / P95 (ou P99) do RTT do fluxo |
| `razao_jitter_p95` | jitter atual / P95 do jitter do fluxo |
| `amplitude_rtt_rel` | (RTT máx − RTT mín) / RTT médio |
| `delta_ttl_clip` | TTL atual − `ttl_baseline`, limitado a ±16 |
| `ttl_reset` | 1 se \|ΔTTL\| ≥ 64 |
| `perda_pct` | (enviados − recebidos) / enviados × 100 |
| `rtt_ausente` | 1 se não há RTT utilizável |

| Situação | Conta |
| -------- | ----- |
| RTT ausente | Razões vazias; `rtt_ausente = 1`; nunca 0 ms |
| Denominador zero ou vazio | Razão vazia |
| Variável vazia no dataset final | Sentinela −1 (só nas que dependem de RTT) |

**Resultado:** 328.421 medições do Período B em 131 fluxos.

## 4. Tabela de rotulagem — parar na primeira linha verdadeira

| Ordem | Classe | Condição | Medições |
| ----- | ------ | -------- | -------- |
| 1 | **FALHA** | perda ≥ 200/3 (2 de 3 pacotes) | 2.450 |
| 2 | **FALHA** | RTT > P99 do próprio fluxo | 10.975 |
| 3 | **RISCO** | perda ≥ 100/3 (1 de 3 pacotes) | 769 |
| 4 | **RISCO** | RTT > P95 do próprio fluxo | 17.778 |
| 5 | **RISCO** | jitter > P95 do próprio fluxo | 11.513 |
| 6 | **OK** | nenhuma linha anterior | 284.936 |

Fluxo com pelo menos 50% das linhas acima do P99 tem baseline desatualizado e fica sem rótulo. Nesta coleta: **nenhum**.

- [x] Três exemplos auditáveis
- [x] Contagem OK / RISCO / FALHA no Período B
- [x] A classe **não** foi definida por limiar global de RTT nem pela rota: os limites são o P95 e o P99 de cada fluxo
- [x] O Período A não foi rotulado
- [x] Dicionário v0.2 lista as colunas proibidas no modelo: `anchor_id`, `probe_id`, `id_fluxo`, timestamp, RTT absoluto (`rtt_ms`, `rtt_min`, `rtt_avg`, `rtt_max`), `jitter_ms`, `ttl`, `ttl_baseline`, percentis do baseline, `classe`, `classe_atual`, `motivo_rotulagem`, `regra`, `split`, país e rota

**Contagem OK / RISCO / FALHA:** 284.936 / 30.060 / 13.425 (86,76% / 9,15% / 4,09%)

**Evidências (três linhas reais):**

| | OK | RISCO | FALHA |
|---|---|---|---|
| `id_fluxo` | `7222_4377` | `7206_4523` | `7416_2581` |
| Destino (auditoria) | Lahore/PK | Astana/KZ | Dubai/AE |
| Timestamp (UTC) | 01/10/2026 04:15:47 | 03/10/2026 11:43:08 | 30/09/2026 12:37:02 |
| RTT (ms) | 317,53 | 239,33 | 273,91 |
| P95 / P99 do RTT (ms) | 328,42 / 351,95 | 236,49 / 257,36 | 299,00 / 477,66 |
| Jitter / P95 do jitter (ms) | 0,19 / 3,80 | 8,28 / 1,55 | 0,00 / 7,18 |
| `perda_pct` | 0 | 0 | 66,7 |
| Regra que disparou | 6 (OK) | 4 (RTT > P95) | 1 (perda 2 de 3) |

## 5. Alvo, variáveis e recorte (ainda sem treinar)

- **Alvo:** classe da **próxima** medição do mesmo fluxo, só se o intervalo até ela for de no máximo 600 s.
- **21 variáveis:** as 8 instantâneas acima, `perda_media_wN`, `rtt_p95_max_wN`, `jitter_p95_max_wN` e `n_rtt_acima_p95_wN` para N = 3, 6 e 12, e `perdas_consecutivas`. Usam só o presente e o passado do fluxo.
- **Recorte cronológico:** treino até o dia 5 do B, validação até o dia 6, teste depois, com **embargo de 60 min** após cada corte.
- **Fluxos não vistos (Tarefa 5):** 10% dos fluxos (**13**) sorteados com a SEED 42 antes de qualquer resultado, fora de treino, validação e teste (lista em `corte_temporal.json`).

- [x] Treino = trecho mais antigo; validação = meio; teste = mais recente
- [x] Nenhum registro do Período A no treino
- [x] Corte com data e N de cada bloco

**Linhas descartadas:** 131 sem medição seguinte, 11 com intervalo acima de 600 s e 3.511 dentro dos embargos.

| Bloco | Janela (a partir de t0 ≈ 28/09/2026 18:00 UTC) | OK | RISCO | FALHA | N | Fluxos |
|---|---|---|---|---|---|---|
| Treino | t0 → t0 + 5 dias | 182.357 | 18.732 | 9.951 | **211.040** | 118 |
| Validação | t0 + 5 d + 60 min → t0 + 6 d | 35.530 | 3.594 | 1.527 | **40.651** | 118 |
| Teste | t0 + 6 d + 60 min → 05/10/2026 18:00 | 34.783 | 4.236 | 1.434 | **40.453** | 118 |
| Não vistos | todo o B | 29.200 | 3.157 | 267 | 32.624 | 13 |

Datas exatas em `data/processed/corte_temporal.json`.

## 6. Scrum e diário

- [X] Board atualizado

**Link do board:** _https://github.com/users/GzTop1/projects/1_

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
| ---------- | ---------------------- | ------------ | ----------------------------- |
| Isaac William Braz | Não atuei diretamente nesta tarefa (responsável: Davi). | — | — |
| Fernanda Akemi Martins Sanpei | Não atuei diretamente nesta tarefa (responsável: Davi). | — | — |
| Geziel de Andrade | Não atuei diretamente nesta tarefa (responsável: Davi). | — | — |
| Hendrick Ambriola | Não atuei diretamente nesta tarefa (responsável: Davi). | — | — |
| Davi Gabriel Borges dos Santos | Inspeção do bruto; ficha de baseline P95/P99 só com o Período A (mínimo de 30 RTT) e conferência com interpolação manual; métricas relativas do Período B; rótulo na ordem da tabela; alvo t+1, 21 variáveis, corte com embargo e sorteio dos fluxos não vistos; dicionário v0.2. | Garantir que o percentil conferido à mão batesse com o do numpy e que nenhuma janela usasse medições do bloco seguinte. | Manter a ficha congelada e o corte único para as Tarefas 3 a 5. |
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
