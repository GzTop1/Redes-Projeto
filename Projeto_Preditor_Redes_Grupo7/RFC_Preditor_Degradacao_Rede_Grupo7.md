# RFC: Preditor de degradação de rede relativo ao baseline do fluxo — Grupo 7

**Equipe:** Grupo 7 — Isaac William Braz, Fernanda Akemi Martins Sanpei, Geziel de Andrade, Hendrick Ambriola, Davi Gabriel Borges dos Santos, Victor Gabriel Alves  
**Repositório GitHub:** https://github.com/GzTop1/Redes-Projeto  
**Notebook de referência:** `Projeto_Preditor_Falhas_PPF_corrigido_v3.ipynb` (todos os números deste documento vêm da execução de 11/10/2026)

> Um RFC formaliza o problema, o contrato dos dados e o critério de decisão antes de se investir no classificador. O projeto segue o pipeline de referência da professora (`preditor_redes-main`, etapas 1 a 8). A etapa 9 (monitoramento) e a pasta `producao/` não fazem parte do trabalho.

---

## 1. Resumo

O projeto constrói um classificador de três estados (**OK**, **RISCO** e **FALHA**) para medições de ping IPv4 entre uma sonda de origem e uma âncora de destino do RIPE Atlas. O alvo é a **classe da próxima medição do fluxo**, cerca de 4 minutos à frente. A classe é definida em relação ao próprio histórico do fluxo (Período A): perda de pacotes e RTT ou jitter acima do P95 e do P99 daquele fluxo.

A distância da rota entra na física do RTT, mas não entra na classe. Um fluxo curto com mediana de 0,80 ms e um fluxo longo com mediana de 451,57 ms são, cada um, o "normal" de si mesmos. O modelo lê só razões ao baseline do fluxo, perda, TTL e janelas do passado recente.

**Resultado no teste temporal (aberto uma vez):** F1 macro de **0,7675**, contra **0,7302** da persistência ("repetir a classe atual") e 0,3082 da classe majoritária. O ganho vem de manter a classe quando ela não muda. Nos inícios de FALHA, o recall é de **0,0195** (8 de 411). Por isso o modelo funciona como um **detector suavizado**, não como um alerta antecipado.

---

## 2. Contexto e motivação

Uma rede em operação precisa distinguir quatro coisas que aparecem juntas numa série de ping:

1. **Latência estrutural.** Mais quilômetros aumentam o RTT mesmo com o caminho saudável. Na nossa coleta, as medianas de RTT do Período A vão de 0,80 ms (fluxo `7326_1526`) a 451,57 ms (fluxo `6506_2581`).
2. **Degradação.** O caminho responde, mas piorou em relação a si mesmo: RTT acima do P95 ou do P99 do fluxo, jitter acima do P95 do fluxo ou perda parcial.
3. **Indisponibilidade.** Perda de 2 ou 3 dos 3 pacotes.
4. **Mudança de rota.** O RTT muda de patamar e permanece. O enlace pode estar saudável; quem envelheceu foi o baseline. Fluxos em que 50% ou mais das linhas ficam acima do P99 são tratados como baseline desatualizado e saem do dataset (nenhum caso nesta coleta).

Tratar "RTT alto" como falha ensina geografia. Na árvore de contraste da Tarefa 3, um modelo que só via RTT absoluto e rota caiu para F1 macro de 0,5279 na validação, contra 0,7691 da árvore com variáveis relativas.

O usuário do alerta é quem opera o enlace: investigar (FALHA), observar (RISCO) ou não agir (OK). O alerta não é uma ordem de intervenção.

---

## 3. Problema e evento a ser previsto

| Pergunta | Resposta do grupo |
|---|---|
| Qual evento será previsto? | A **classe da próxima medição** de ping de um fluxo: OK, RISCO ou FALHA. |
| Como a classe é definida? | Regra por fluxo, na ordem da seção 8.4: perda e RTT/jitter comparados ao P95/P99 do próprio fluxo no Período A. |
| Qual é o horizonte? | Uma medição à frente (240 s), só se o intervalo até ela for de no máximo 600 s. |
| Qual é a unidade de análise? | Uma execução de ping (3 pacotes) de um fluxo, com as janelas de 3, 6 e 12 medições anteriores do mesmo fluxo. |
| O que é um fluxo? | `id_fluxo = {probe_id}_{anchor_id}` (exemplo: `6411_1070`). |
| Contra o que é comparado? | Persistência (a classe atual como previsão da próxima) e classe majoritária. A classe atual **não** é variável do modelo. |

| Classe | Significado operacional |
|---|---|
| **OK** | Perda nula, RTT e jitter dentro do P95 do fluxo. |
| **RISCO** | 1 de 3 pacotes perdido, ou RTT acima do P95, ou jitter acima do P95. |
| **FALHA** | 2 ou 3 de 3 pacotes perdidos, ou RTT acima do P99 do fluxo. |

---

## 4. Escopo

| Pergunta | Resposta do grupo |
|---|---|
| Recorte | Ping IPv4 público do *Anchoring Mesh* do RIPE Atlas. **30 âncoras de destino** (1 no Brasil e 29 países distintos, cotas por continente, máximo de 6 na Europa, 1 por ASN, faixas de distância < 4.000 km, < 10.000 km e ≥ 10.000 km, sorteio com SEED 42). **3 a 5 sondas por destino** escolhidas por diversidade de ASN, faixa, continente e país: **150 fluxos**, 129 sondas distintas. |
| Período | Período A (baseline): 21/09/2026 18:00 a 28/09/2026 18:00 UTC. Período B (dataset): 28/09/2026 18:00 a 05/10/2026 18:00 UTC. Janelas em hora cheia, sem sobreposição. Os resultados foram baixados em 11/10/2026 do endpoint histórico `/results/`. |
| Cobertura | Um fluxo só entra em um período com pelo menos 80% das 2.520 execuções esperadas (2.016) e, no A, com pelo menos 30 TTL válidos. Só fluxos **A+B** seguem para o modelo: **131 de 150**. |
| Dentro do escopo | `GET` público; JSON bruto preservado; baseline congelado; variáveis relativas; rótulo por regra; split temporal com embargo; fluxos não vistos sorteados antes do treino; comparação com persistência e classe majoritária; ficha do modelo; teste de equivalência com o código da professora. |
| Fora de escopo | `POST` e créditos do RIPE Atlas. IPv6, traceroute, HTTP. Limiar global de RTT. País, IP, rota ou `id_fluxo` como variável. Trocar destinos depois de coletar. RTT ausente gravado como 0. Split aleatório. Etapa 9 (monitoramento). |

---

## 5. Usuários e decisão apoiada

Com **FALHA**, a ação é investigar perda ou latência extrema. Com **RISCO**, observar e priorizar. Com **OK**, nada. Um fluxo novo só pode ser classificado depois de um Período A próprio com pelo menos 30 RTT válidos e cobertura mínima de 80%.

---

## 6. Dados e fontes

| Fonte | O que fornece | Papel |
|---|---|---|
| RIPE Atlas v2: `/anchors/`, `/anchor-measurements/`, `/measurements/`, `/probes/` | Âncoras, medições mesh, sondas participantes | Desenho (`config/anchors_selecionadas.json`, `medicoes_ping_ongoing.json`, `tabela_desenho.csv`) |
| `/measurements/{msm_id}/results/` | Timestamp, sonda, RTT dos 3 pacotes, enviados, recebidos, TTL | Bruto: **420 arquivos JSON** em `data/raw/` (331,4 MB), 30 medições × 14 dias |
| Período A | P95/P99 de RTT e jitter, mediana do TTL | `baseline_por_fluxo.csv` (congelado) |
| Período B | 21 variáveis, classe atual, alvo t+1, bloco | `dataset_final.csv` |

**Volume observado:**
- **695.132 registros** na tabela de trabalho (345.094 no A e 350.038 no B), em 141 fluxos com resultado.
- RTT ausente (timeout) em 4,51% das linhas, sempre vazio, nunca 0. TTL presente em 95,5%. Duplicatas: 0.
- 61 medições de ping IPv4 Ongoing para as 30 âncoras; todos os 30 ids mesh conferidos.
- **131 fluxos com baseline VÁLIDO.** 19 fluxos excluídos por cobertura (motivos em `config/exclusoes_fluxos.csv`). Os destinos 4227 (Changhua/TW) e 4862 (Antananarivo/MG) ficaram sem fluxo utilizável.
- Período B rotulado: **328.421 medições**, sendo 86,76% OK, 9,15% RISCO e 4,09% FALHA.

Jitter: desvio-padrão **populacional** dos RTT da execução; 0 com uma resposta; vazio sem RTT.

País, IP, rota, faixa de distância e ASN ficam só em `config/tabela_desenho.csv`, para auditoria.

---

## 7. Custo dos erros

| Tipo de erro | O que significa | No teste |
|---|---|---|
| Falso negativo de FALHA | FALHA real prevista como OK ou RISCO. **O erro mais grave.** | 488 de 1.434 (253 como OK, 235 como RISCO); recall de FALHA 0,6597 |
| Falso negativo de RISCO | RISCO real previsto como OK | 2.097 de 4.236; recall de RISCO 0,4681 |
| Falso positivo de FALHA | OK ou RISCO previsto como FALHA | 202 (46 OK, 156 RISCO); precisão de FALHA 0,8240 |
| Falso positivo de RISCO | OK previsto como RISCO | 105 |

A métrica de seleção é o **F1 macro** (igual à `METRICA_SELECAO` da professora). Recall de FALHA, fatia de transições e fatia de início de falha são reportados à parte. A acurácia (0,9285 no teste) não decide, porque 86% das linhas são OK.

---

## 8. Abordagem

Ingestão → Período A só para baseline → congelamento → variáveis relativas no Período B → rótulo → alvo t+1 → split temporal com embargo e fluxos não vistos → grade de três famílias escolhida na validação → teste único → ficha do modelo.

### 8.1 Baseline por fluxo (só Período A)

| Campo | Cálculo |
|---|---|
| `n_amostras_A`, `n_rtt_validos_A` | execuções e RTT válidos no A |
| `mediana_rtt_A`, `p95_rtt_A`, `p99_rtt_A` | mediana e percentis (interpolação linear) do RTT médio |
| `mediana_jitter_A`, `p95_jitter_A`, `p99_jitter_A` | mesmo para o jitter |
| `ttl_baseline` | mediana do TTL |
| `status_baseline` | `VALIDO` se há pelo menos 30 RTT válidos |

Conferência com numpy: fluxo curto `7326_1526` (mediana 0,80 ms, P95 0,91, P99 1,05) e longo `6506_2581` (mediana 451,57 ms, P95 489,87, P99 656,78).

### 8.2 Variáveis (21)

| Grupo | Variáveis |
|---|---|
| Instantâneas (8) | `perda_pct`, `rtt_ausente`, `razao_rtt_p95`, `razao_rtt_p99`, `razao_jitter_p95`, `amplitude_rtt_rel`, `delta_ttl_clip` (±16), `ttl_reset` (\|ΔTTL\| ≥ 64) |
| Janelas de 3, 6 e 12 medições (12) | `perda_media_wN`, `rtt_p95_max_wN`, `jitter_p95_max_wN`, `n_rtt_acima_p95_wN` |
| Persistência (1) | `perdas_consecutivas` |

As janelas usam só a medição atual e o passado do mesmo fluxo. Variáveis que dependem de RTT ausente recebem a sentinela −1 (sem imputar média nem mediana).

### 8.3 Regra de rotulagem (para na primeira verdadeira)

| Ordem | Condição | Classe | Medições no B |
|---|---|---|---|
| 1 | perda ≥ 2 de 3 pacotes | FALHA | 2.450 |
| 2 | RTT > P99 do fluxo | FALHA | 10.975 |
| 3 | perda ≥ 1 de 3 pacotes | RISCO | 769 |
| 4 | RTT > P95 do fluxo | RISCO | 17.778 |
| 5 | jitter > P95 do fluxo | RISCO | 11.513 |
| 6 | nenhuma | OK | 284.936 |

**Mecanismo dominante:** 82% das FALHAs (10.975 de 13.425) vêm da latência acima do P99. Por construção, cerca de 5% e 1% das linhas de um fluxo estável ficam acima do P95 e do P99, então parte de RISCO e FALHA é ruído estatístico, não degradação percebida.

### 8.4 Modelo

Grade e desempate da etapa 8 da professora: maior macro-F1 na validação, depois menor gap treino−validação, depois a família e o modelo mais simples.

| Família | Candidatos | Melhor na validação |
|---|---|---|
| Naive Bayes | 4 | `var_smoothing` 1e-3; macro-F1 0,5223 |
| Árvore de decisão (CART) | 30 | `max_depth` 12, `min_samples_leaf` 100, sem `class_weight`; 220 folhas; macro-F1 0,7691; gap 0,0233 |
| **Random Forest** (escolhido) | 24 | 200 árvores, `max_depth` None, `min_samples_leaf` 5, `max_features` sqrt; macro-F1 **0,7702**; gap 0,0521 |

---

## 9. Avaliação

**Protocolo A — tempo.** A partir da primeira medição do Período B (t0 ≈ 28/09/2026 18:00 UTC): treino até t0 + 5 dias; validação de t0 + 5 dias + 60 min até t0 + 6 dias; teste de t0 + 6 dias + 60 min até o fim do B. O embargo de 60 min tirou 3.511 linhas.

| Bloco | Linhas | Fluxos | OK | RISCO | FALHA |
|---|---|---|---|---|---|
| Treino | 211.040 | 118 | 182.357 | 18.732 | 9.951 |
| Validação | 40.651 | 118 | 35.530 | 3.594 | 1.527 |
| Teste | 40.453 | 118 | 34.783 | 4.236 | 1.434 |
| Não vistos | 32.624 | 13 | 29.200 | 3.157 | 267 |

**Protocolo B — fluxos novos.** 10% dos fluxos (13) sorteados com a SEED antes de qualquer treino, fora de treino, validação e teste, cada um com o próprio baseline do Período A.

**Resultados:**

| Avaliação | F1 macro | Recall FALHA | Observação |
|---|---|---|---|
| Persistência (validação) | 0,7261 | 0,7341 | Referência |
| Árvore T3 (validação) | 0,7691 | 0,7046 | — |
| Random Forest T4 (validação) | 0,7702 | 0,7073 | Escolhido |
| **Teste — modelo final** | **0,7675** | **0,6597** | Balanced accuracy 0,7078 |
| Teste — persistência | 0,7302 | — | Modelo +0,0373 |
| Teste — classe majoritária (OK) | 0,3082 | 0 | — |
| Teste — transições (classe muda) | 0,2344 | — | — |
| Teste — início de FALHA (411 casos) | — | 0,0195 | Quase nada antecipado |
| Não vistos — modelo | 0,6275 | 0,2659 | Persistência 0,6207 |

Nos fluxos não vistos, por faixa de distância: na **curta**, 0 de 270 degradações foram detectadas; na média, 108 de 914; na longa, 1.347 de 2.240.

---

## 10. Riscos e limitações

- **Rótulos são uma política, não um defeito confirmado.** A classe é relativa ao P95/P99 do próprio fluxo. Em um fluxo estável, cerca de 5% das linhas ultrapassam o P95 por definição.
- **O modelo não antecipa falhas.** Recall de 0,0195 nos inícios de FALHA; 87% dos erros da validação acontecem quando a classe muda.
- **Generalização fraca em caminhos curtos.** Nos fluxos não vistos, nenhuma degradação da faixa curta foi detectada.
- **Todas as sondas de origem são âncoras.** As medições mesh só têm âncoras como participantes, então a preferência por sonda comum (`MIN_PROBES_COMUNS = 1`) nunca teve efeito. Último quilômetro e redes de acesso ficam de fora.
- **3 pacotes por execução:** a perda só assume 0, 33, 67 ou 100%, e o jitter é estimado com no máximo 3 valores.
- **Baseline fixo** não acompanha deriva lenta.
- **Teste curto:** um único bloco de cerca de 1 dia.
- **Fluxos não independentes:** a mesma sonda serve vários destinos, e amostras a cada 4 min são autocorrelacionadas.
- **Cobertura:** 19 fluxos e 2 destinos ficaram fora.
- **Modelo final não é interpretável por regras** (Random Forest). As regras legíveis são as da árvore da Tarefa 3, com F1 macro de validação 0,7691.

---

## 11. Critérios de sucesso

| # | Critério | Situação |
|---|---|---|
| 1 | Baseline só do Período A; nenhuma variável usa país, IP, rota ou RTT absoluto | **Atendido** (conferido por código na 5.1) |
| 2 | F1 macro acima da classe majoritária, com recall de FALHA explícito | **Atendido:** 0,7675 contra 0,3082; recall de FALHA 0,6597 |
| 3 | Modelo supera a persistência | **Atendido no geral** (+0,0373), **não atendido nos inícios de FALHA** (recall 0,0195) |
| 4 | Fluxos novos com baseline próprio | **Parcial:** F1 0,6275 contra 0,6207; faixa curta sem detecção |
| 5 | Teste aberto uma vez | **Atendido:** `teste_unico.json` (11/10/2026 14:35 UTC); as execuções seguintes só leem o arquivo |
| 6 | Equivalência com o pipeline da professora | **Atendido:** 123 de 123 verificações idênticas (`config/teste_equivalencia_professora.csv`) |

---

## 12. Alternativas consideradas

| Alternativa | Por que foi rejeitada |
|---|---|
| Limiar global de RTT | A classe vira distância. |
| Árvore com RTT absoluto e rota | Contraste da Tarefa 3: F1 macro 0,5279, contra 0,7691 da árvore oficial. Descartada. |
| Mediana/MAD/z-robusto e piso de 1.500 RTT | Com MAD de fração de milissegundo, variações mínimas viram FALHA. Adotados o baseline P95/P99 e o mínimo de 30 RTT do pipeline de referência. |
| Alvo = classe atual | O modelo apenas reproduziria a regra de rótulo. O alvo t+1 mede previsão de fato. |
| Trocar destinos sem resposta depois de coletar | Introduz viés de seleção. Adotada a exclusão registrada por cobertura mínima de 80%. |
| Split 50/20/30 por fração | Cortes fixos nos dias 5 e 6 com embargo de 60 min evitam que janelas do mesmo fluxo cruzem blocos. |
| `class_weight` balanced | Subiu o recall de RISCO (0,42 → 0,57) e de FALHA (0,70 → 0,76), mas derrubou o F1 macro para 0,6828. Fica como opção se a operação priorizar recall. |
| Split aleatório | Vazaria janelas do mesmo fluxo entre treino e teste. |

---

## 13. Perguntas em aberto

1. **Modelo entregue:** o Random Forest venceu a árvore por apenas +0,0011 de F1 macro na validação; a árvore é a alternativa interpretável.
2. **Antecipação:** variáveis de tendência ou horizonte maior podem melhorar o recall nos inícios de FALHA.
3. **Ruído do rótulo:** exigir persistência (por exemplo, 2 de 3 medições acima do P95) antes de marcar RISCO.
4. **Caminhos curtos:** investigar por que nenhuma degradação curta dos fluxos não vistos foi detectada.
5. **Baseline móvel** quando houver série maior que 7 + 7 dias.

---

## 14. Encadeamento

| Etapa | Produz | A etapa seguinte usa |
|---|---|---|
| Coleta (Tarefa 1) | `data/raw/` (420 JSON), `config/` (âncoras, medições, `tabela_desenho.csv`, `relatorio_qualidade_fluxos.csv`, `exclusoes_fluxos.csv`, `fluxos_modelagem.csv`, `parametros.json`), `data/interim/bruto_tabela.csv` | Este bruto |
| Baseline e rótulo (Tarefa 2) | `baseline_por_fluxo.csv`, `dataset_final.csv`, `corte_temporal.json` | Estes rótulos e este corte |
| Primeira árvore (Tarefa 3) | `modelos/arvore_T3.joblib` | Os erros da validação |
| Ajuste (Tarefa 4) | `modelos/modelo_T4.joblib`, `grade_busca.csv`, `tabela_T3_T4.csv` | Este modelo |
| Modelo final (Tarefa 5) | `modelo_final_congelado.json`, `teste_unico.json`, `ficha_do_modelo.json`, `requirements.txt` | — |

Não se rotula o período que estimou o baseline. Não se sorteia linha para o teste.
