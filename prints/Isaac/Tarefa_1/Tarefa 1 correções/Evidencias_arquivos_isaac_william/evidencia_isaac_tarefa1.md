# Evidência individual — Tarefa 1 (Parte 0 e seções 1.1 a 1.6)

**Autor:** Isaac William Braz (Scrum Master da Tarefa 1)  
**Data e hora da execução:** 11/10/2026 14:04 UTC, Google Colab  
**Fonte de verdade:** modelo da professora (`preditor_redes-main`), etapas 1 a 5  
**Ferramentas de apoio:** Claude (IA da Anthropic) como apoio para ler o código da professora e reescrever as funções; a execução no Colab, a conferência das saídas e a decisão de seguir o modelo dela foram feitas por mim

| Código | Seção | Antes (primeira versão) | Depois (corrigido) | Evidência gerada nesta execução | Fonte no modelo da professora |
|---|---|---|---|---|---|
| C01 | 1.1 | alvo era o estado atual (e +12 min); fluxo identificado por probe e IP | alvo = classe da próxima medição; fluxo `probe_id_anchor_id` | exemplo de id_fluxo: 6411_1070 | `pipeline/07_rotulagem/src/rotular_e_gerar_final.py: preparar_serie() (alvo t+1); pipeline/06_baseline/src/config.py: FORMATO_ID_FLUXO = {probe_id}_{anchor_id}` |
| C02 | 1.2 | 7 países fixos, 2 âncoras por país, menor `id` | 30 âncoras estratificadas (1 BR + 29 países, cotas por continente, máx. 1 por ASN, faixas, SEED) | 30 países distintos; ASN máximo 1; continentes {'América do Norte': 3, 'América do Sul': 7, 'Europa': 6, 'Oceania': 2, 'África': 5, 'Ásia': 7}; faixas {'curta': 8, 'media': 11, 'longa': 11} | `pipeline/01_anchors/src/selecionar_anchors.py: preparar_anchors(), selecionar(), validar(); pipeline/01_anchors/src/config.py: FAIXAS_KM, COTAS_CONTINENTE, MAX_ANCHORS_POR_ASN, SEED` |
| C03 | 1.3 | filtro pelo texto "Anchoring Mesh"; quebrava com 2 medições | medição mesh por /anchor-measurements/, conferida por fqdn e IP | 61 medições para 30 âncoras; mesh conferido 30/30 | `pipeline/01_anchors/src/selecionar_anchors.py: indexar_medicoes(), medicao_ping_ipv4_publica(); pipeline/02_medicoes/src/buscar_medicoes.py: compativel(), processar()` |
| C04 | 1.4 | 4 âncoras do país de origem por ordem de `id`; só BR e DE | 3 a 5 sondas por destino, por diversidade e faixa de distância, sem auto-ping | 150 fluxos, 129 sondas distintas, 30 destinos; faixas {'longa': 65, 'media': 55, 'curta': 30} | `pipeline/03_probes/src/selecionar_probes.py: ids_participantes(), escolher(), selecionar(); pipeline/03_probes/src/config.py: MIN_PROBES=3, MAX_PROBES=5` |
| C05 | Parte 0 | o retry repetia erro 404; sem cache | repete só 429/5xx/rede; cache de 24 h | 420 arquivos de coleta gravados sem repetir os já existentes | `pipeline/03_probes/src/selecionar_probes.py: obter_json() com cache e repetição só em 429/5xx; pipeline/03_probes/src/config.py: MAX_TENTATIVAS, CACHE_TTL_HORAS` |
| C06 | Parte 0 | início às 04:32, sem hora cheia | janelas fixas em hora cheia UTC; fim do A = início do B | A 21/09 18:00 -> 28/09 18:00; B -> 05/10 18:00 UTC | `pipeline/05_periodos/src/config.py: PERIODOS (janelas fixas em hora cheia UTC, A termina onde B começa)` |
| C07 | 1.6 | `ttl` descartado; jitter amostral (ddof=1) | guarda `ttl`; jitter populacional (ddof=0) | 695.132 registros em 141 fluxos; coluna ttl preenchida em 95.5% das linhas | `pipeline/05_periodos/src/processar_dataset.py: feature_jitter_ms() (pstdev), feature_ttl(), feature_perda_pct()` |
| C08 | 1.6-A | piso de 1.500 RTT; troca de destinos depois de coletar | cobertura mínima de 80% (2016 de 2520); classes A+B/B/A/nenhum; exclusão registrada | classes {'A+B': 131, 'nenhum': 11, 'B': 8}; 19 fluxos excluídos; destinos sem fluxo utilizável: [4227, 4862] | `pipeline/05_periodos/src/coletar_periodos.py: classificar_periodo(), classe_do_fluxo(); pipeline/05_periodos/src/config.py: COBERTURA_MINIMA_PERCENT = 80` |

**Resumo da coleta:** 420 arquivos JSON em `data/raw/` (30 medições × 14 dias); 131 de 150 fluxos seguem para o modelo (classe A+B).

Onde conferir no notebook: seções 1.1 a 1.6-A, `config/evidencias.jsonl`, `config/correcoes_com_fonte_professora.csv` e `config/teste_equivalencia_professora.csv`.