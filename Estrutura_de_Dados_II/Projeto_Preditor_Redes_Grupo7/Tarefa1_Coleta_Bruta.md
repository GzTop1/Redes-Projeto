# Diário da Tarefa 1 — Problema e coleta bruta (sem rótulo)

**Período:** 21/09/2026 a 05/10/2026  
**Projeto:** Preditor de qualidade de rede (RIPE Atlas): classe da próxima medição de um fluxo  
**Modelo desta disciplina:** árvore de decisão. Nesta tarefa não se treina árvore.

**Equipe:** Grupo 7  
**Integrantes:** Isaac William Braz, Fernanda Akemi Martins Sanpei, Geziel de Andrade, Hendrick Ambriola, Davi Gabriel Borges dos Santos  
**Scrum Master da tarefa:** Isaac William Braz  
**Repositório GitHub:** [Redes-Projeto](https://github.com/GzTop1/Redes-Projeto)

> Esta tarefa entrega o problema e o **dado cru**. Não há classe OK, RISCO ou FALHA. Não há baseline, não há mediana e não há árvore. Quem rotular aqui mistura a coleta com a decisão da Tarefa 2.
>
> A rota entra na coleta só para haver caminhos curtos, médios e longos nas 30 âncoras estratificadas. RTT alto **não** é falha. País, IP e nome da rota **não** serão coluna da árvore.

### Contrato desta tarefa

| | Artefato | Quem usa depois |
|---|---|---|
| **Entra** | Modelo da professora (`preditor_redes-main`, etapas 1 a 5) | — |
| **Sai** | Estrutura de diretórios `config/` e `data/raw/` | Tarefas 2 a 5 **usam este bruto** |
| **Sai** | Dicionário v0.1 só com colunas **brutas** da medição | Tarefa 2 |
| **Sai** | 420 arquivos de coleta e relatório de qualidade | Tarefa 2 e seguintes |
| **Sai** | Este diário atualizado com os valores reais da execução | Tarefas seguintes |

**Não sai daqui:** baseline, rótulo, `z_robusto`, split, árvore, métrica de modelo.

---

## 1. Definição do problema

Responder no diário. A resposta tem de bater com o código e as configurações validadas.

| Pergunta | Resposta do grupo (com base na execução real) |
|---|---|
| Qual evento a árvore vai classificar? | A **classe da próxima medição** de ping de um fluxo (`OK`, `RISCO` ou `FALHA`). |
| O que é um fluxo? | Um par `probe_id` + `anchor_id` (exemplo: `6411_1070`), com 131 fluxos aprovados na cobertura `A+B`. |
| O que é cada linha do bruto? | Uma execução de ping (3 pacotes), publicada a cada 240 s, ainda **sem** classe. |
| Qual horizonte fica para depois? | Uma medição à frente (cerca de 4 minutos). A árvore só entra na Tarefa 3. |
| Quem usa o alerta? | Quem opera o enlace: investigar (FALHA), observar (RISCO) ou não agir (OK). |
| O que está proibido como definição de falha? | Limiar global de RTT, país, continente ou nome da rota. |

- [x] Parâmetros validados conforme o modelo da professora (etapas 1 a 5)
- [x] Dicionário v0.1 só com variáveis brutas (notebook, seção 1.7)

## 2. O que coletar (e o que não criar)

Fonte: medições públicas já existentes de ping IPv4 (mesh de Anchors do RIPE Atlas, somente `GET`). Não criar medição própria e não gastar crédito.

| Campo | Unidade | Papel agora | No notebook |
|---|---|---|---|
| `timestamp` | UTC | Ordenar o fluxo | `timestamp` |
| `measurement_id` | — | Identidade da medição | `msm_id` |
| `probe_id` | — | Origem | `probe_id` |
| `anchor_id` | — | Destino | `anchor_id` |
| `id_fluxo` | texto estável | `{probe_id}_{anchor_id}` | `id_fluxo` |
| RTT da rajada (médio; mín/máx) | ms | Vazio se não houver resposta. **Nunca 0** | `rtt_min`, `rtt_avg`, `rtt_max` |
| enviados, recebidos | contagem | | `sent`, `rcvd`, `n_rtt` |
| `perda_pct` | % | `(enviados − recebidos) / enviados × 100` | `perda_pct` |
| `jitter_ms` | ms | Desvio-padrão **populacional** dos RTT da rajada | `jitter_ms` (pstdev) |
| `ttl` | — | TTL da resposta | `ttl` |

Regras da coleta:

- [x] 30 âncoras estratificadas (1 BR + 29 países, cotas por continente, máx. 1 por ASN, faixas de distância e `SEED`)
- [x] 150 fluxos selecionados por diversidade (3 a 5 probes por destino, sem auto-ping)
- [x] Dois blocos de tempo fixos em hora cheia UTC: Período A de `21/09/2026 18:00` a `28/09/2026 18:00 UTC`; Período B de `28/09/2026 18:00` a `05/10/2026 18:00 UTC`
- [x] Timeout preservado no arquivo e na tabela tratada
- [x] JSON bruto preservado em `data/raw/` com gravação atômica e idempotente (cache de 24h, repetição apenas em erros transitórios 429/5xx/rede)
- [x] Parâmetros em `config/` (`anchors_selecionadas.json`, `tabela_desenho.csv`, `evidencias.jsonl`, etc.)
- [x] `requirements.txt` da coleta (pandas, numpy, requests)

**Desenho da coleta (Execução Real):**

| Categoria | Detalhe | Quantidade |
|---|---|---|
| Âncoras | 30 âncoras IPv4 (1 BR + 29 países) | 30 |
| Continentes | América do Sul (7), Ásia (7), Europa (6), África (5), América do Norte (3), Oceania (2) | 6 continentes |
| Faixas de distância | Curta (8), Média (11), Longa (11) | 3 faixas |
| Sondas de origem | 129 sondas distintas | 129 probes |
| Fluxos gerados | Pares `probe_id_anchor_id` | 150 fluxos |

**Decisão documentada:** nenhum destino foi trocado depois da coleta. Cada fluxo só entra em um período com cobertura mínima de 80% (2.016 de 2.520 execuções) e, no Período A, com pelo menos 30 TTL válidos. Os fluxos que não atingem esse mínimo são **excluídos**, com o motivo registrado em `config/exclusoes_fluxos.csv`. Resultado: 131 fluxos na classe `A+B` seguem para a modelagem; os destinos 4227 (Changhua/TW) e 4862 (Antananarivo/MG) ficaram sem fluxo utilizável e foram mantidos como exclusão declarada, não substituídos.

**Evidências (notebook, commit, trecho do config):** notebook `Estrutura_de_Dados_II/Projeto_Preditor_Redes_Grupo7/Projeto_Preditor_Falhas_PPF.ipynb`, seções 1.1 a 1.6-A; `config/correcoes_com_fonte_professora.csv`; `config/evidencias.jsonl`.

## 3. Relatório de qualidade — ainda sem classe

- [x] Registros totais gerados: **695.132 registros em 141 fluxos** processados na tabela de trabalho.
- [x] Coluna `ttl` preenchida em **95,5% das linhas**.
- [x] Duplicatas: 0.
- [x] RTT e perda descritos **sem** dizer OK, RISCO ou FALHA.
- [x] Cobertura mínima de 80% aplicada: 131 fluxos na classe `A+B`, 8 na classe `B`, 11 na classe `nenhum` (19 fluxos excluídos com registro em `config/exclusoes_fluxos.csv`).

**N de arquivos brutos:** 420 arquivos JSON gravados em `data/raw/` (30 medições × 14 dias).

## 4. Scrum

- [x] Product Owner = Fernanda Akemi Martins Sanpei, indicada pelo grupo; Scrum Master da tarefa = Isaac William Braz; time de desenvolvimento = os demais integrantes do Grupo 7
- [x] Board com To do / Doing / Done atualizado no GitHub
- [x] Pelo menos 3 histórias: coletar 30 âncoras estratificadas; preservar o bruto com cache e retentativa refinada; separar Período A e Período B em hora cheia sem rotular.

**Histórias:**  
1. Como grupo, quero coletar 30 âncoras estratificadas por continente e faixa de distância, para garantir diversidade geográfica sem viés de rota. *Critério de aceite:* 30 âncoras e 150 fluxos validados.  
2. Como grupo, quero preservar o JSON bruto com cache de 24h e retentativa apenas em erros transitórios, para garantir idempotência e robustez na ingestão. *Critério de aceite:* 420 arquivos em `data/raw/` salvos de forma atômica.  
3. Como grupo, quero separar os Períodos A e B em hora cheia UTC com cobertura mínima de 80%, para que o baseline seja construído com dados confiáveis e sem rótulos. *Critério de aceite:* 131 fluxos classificados como `A+B`.

**Link do board:** *https://github.com/users/GzTop1/projects/1*

## 5. Diário de bordo

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Isaac William Braz | Alinhamento completo com o modelo da professora (etapas 1 a 5); configuração das 30 âncoras estratificadas; busca de medições mesh; seleção de 150 fluxos com base em diversidade e distância; coleta dos 420 arquivos JSON em janelas UTC de hora cheia; processamento da tabela de trabalho (695.132 registros, TTL preenchido em 95,5%); aplicação do filtro de cobertura ≥ 80% (131 fluxos `A+B`); elaboração do dicionário v0.1 e registro de evidências e correções. | Ajuste fino das regras de API REST do RIPE Atlas (cache, tratamento de 429/5xx vs 404) e alinhamento estrito das janelas temporais em hora cheia UTC conforme o pipeline da professora. | Manter a equivalência rigorosa com o código da professora e o rastreio em `config/evidencias.jsonl`. |
| Fernanda Akemi Martins Sanpei | Auxílio na revisão das diretrizes metodológicas e preparação para a Tarefa 3. | — | — |
| Geziel de Andrade | Colaboração na estruturação do repositório e suporte à integração com o GitHub. | — | — |
| Hendrick Ambriola | Preparação para a transição dos dados para a etapa de modelagem (Tarefa 4). | — | — |
| Davi Gabriel Borges dos Santos | Acompanhamento do pipeline de baseline e estruturação da Tarefa 2. | — | — |

## 6. Evidências gerais

- Link do repositório: *https://github.com/GzTop1/Redes-Projeto*
- Link do dicionário v0.1: notebook `Estrutura_de_Dados_II/Projeto_Preditor_Redes_Grupo7/Projeto_Preditor_Falhas_PPF.ipynb`, seção 1.7
- Link dos commits: *https://github.com/GzTop1/Redes-Projeto/commits/main*

---

## Rubrica — Tarefa 1 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Problema | 0,5 | Fluxo, unidade de análise e proibição de RTT absoluto como falha estão explícitos | | |
| Coleta bruta | 1,5 | Vários fluxos (30 âncoras estratificadas), timeout preservado, RTT vazio ≠ 0, config externa, bruto intocável | | |
| Período A e Período B sem rótulo | 1,0 | Dois blocos em hora cheia sem sobreposição; relatório de qualidade **sem** classe | | |
| Scrum + diário | 1,0 | Papéis, board, histórias e diário de todos | | |
| **Total** | **4,0** | | **___ / 4,0** | |
