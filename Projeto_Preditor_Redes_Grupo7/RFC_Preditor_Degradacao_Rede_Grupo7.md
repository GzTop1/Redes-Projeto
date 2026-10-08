# RFC: Preditor de degradação de rede com RTT normalizado — Grupo 7

**Equipe:** Grupo 7 — Isaac William Braz, Fernanda Akemi Martins Sanpei, Geziel de Andrade, Hendrick Ambriola, Davi Gabriel Borges dos Santos, Victor Gabriel Alves  
**Repositório GitHub:** https://github.com/GzTop1/Redes-Projeto  
**Notebook de referência:** `Projeto_Preditor_Falhas_PPF_.ipynb` (todos os números deste documento vêm da execução final, de 07/10/2026)

> Um RFC formaliza o problema, o contrato dos dados e o critério de decisão antes de se investir no classificador. Este documento escolhe a **representação** do fenômeno (RTT normalizado por fluxo). Nesta disciplina, o classificador é uma **árvore de decisão (CART)**, ajustada nas Tarefas 3 e 4 olhando só a validação.

---

## 1. Resumo

O projeto constrói um classificador de três estados — **OK**, **RISCO** e **FALHA** — para medições ICMP de pares origem–destino. O estado descreve o afastamento do fluxo em relação ao seu próprio comportamento normal, estimado num período anterior (Período A) e depois congelado.

A distância da rota entra na física do RTT, mas não entra na classe. Na nossa coleta, um RTT de cerca de 208 ms é o normal de um caminho BR→DE saudável, enquanto um fluxo DE→DE com mediana de cerca de 1,5 ms foi marcado como FALHA ao chegar a 2,2 ms (aumento de 45%, `z_robusto` de 6,4), porque seu desvio típico é de fração de milissegundo. A árvore aprende esse desvio em conjunto com perda, jitter relativo, timeouts e persistência.

**Resultado:** a árvore final separa OK, RISCO e FALHA com **F1 macro de 0,9997** no teste temporal (contra 0,2949 da classe majoritária) e de 0,9997 em fluxos nunca vistos. Ela **não** supera a regra "repetir a classe atual" a 12 minutos, então o entregável é um **detector** do estado atual, não um preditor.

---

## 2. Contexto e motivação

Uma rede em operação precisa distinguir quatro coisas que aparecem juntas numa série de ping:

1. **Latência estrutural.** Mais quilômetros e mais roteadores aumentam o RTT mesmo com o caminho saudável. Na nossa coleta, a mediana do RTT é de 9,63 ms nos caminhos curtos, 36,29 ms nos regionais e 203,91 ms nos longos (BR→DE, BR→JP e BR→US). Esse atraso é esperado, não defeito.
2. **Degradação.** O caminho continua respondendo, mas piorou em relação a si mesmo: RTT acima da variação típica, jitter instável ou perda moderada e persistente.
3. **Indisponibilidade.** Perda total ou ausência persistente de resposta. É falha independentemente da distância.
4. **Mudança de rota.** O RTT muda de patamar e permanece estável, com perda e jitter baixos. O enlace novo pode estar saudável; o que envelheceu foi o baseline.

Tratar "RTT alto" como falha ensina geografia. No Período B desta coleta, **70.342 medições têm RTT acima de 100 ms** (seriam FALHA na regra absoluta antiga) e **77,4% delas são OK** no critério relativo. Na árvore de contraste da Tarefa 3, um modelo que só via RTT absoluto e rota aprendeu um corte fixo de 141,2 ms e caiu para F1 macro de 0,557.

O usuário do alerta é quem opera a rede (campus, provedor ou NOC). O alerta apoia a decisão de investigar o enlace agora, observar, ou recalibrar o "normal" porque o caminho mudou.

---

## 3. Problema e evento a ser previsto

| Pergunta | Resposta do grupo |
|---|---|
| Qual evento será previsto? | Degradação ou indisponibilidade de um fluxo ICMP em relação ao baseline daquele fluxo: OK, RISCO ou FALHA. Não é "rota longa" nem "RTT acima de 100 ms". |
| Como será definida a classe? | Regra híbrida, auditável, relativa ao fluxo (seção 8.4): desvio robusto do RTT, aumento relativo, jitter relativo, perda e persistência em janelas de 5 medições. Os rótulos são operacionais: a árvore reproduz essa política, não um ticket de equipamento. |
| Qual é o horizonte? | **Detector:** classe da medição atual (modelo oficial). **Preditor:** classe 12 minutos à frente (3 intervalos de 240 s), avaliado na Tarefa 5 contra a regra "repetir a classe atual". Resultado: sem ganho, logo o entregável é o detector. |
| Qual é a unidade de análise? | Uma medição de um fluxo, enriquecida com a janela causal recente do mesmo fluxo. O fluxo é `fluxo_id = probe_id \| dst_addr`. |

| Classe | Significado operacional |
|---|---|
| **OK** | RTT, jitter e perda compatíveis com o normal daquele fluxo. |
| **RISCO** | Desvio moderado e persistente de latência ou jitter (2 de 5 medições), ainda sem indisponibilidade. |
| **FALHA** | Desvio extremo, perda elevada ou ausência persistente de resposta. |

O quarto estado operacional, **RECALIBRAR** (mudança estável de patamar), **não foi implementado** nesta entrega; o treino usa só as três classes (ver seções 10 e 13).

---

## 4. Escopo

| Pergunta | Resposta do grupo |
|---|---|
| Recorte | Overlay lógica sobre o *Anchoring Mesh* público do RIPE Atlas (ping IPv4). **8 rotas de desenho**: curtas BR→BR e DE→DE; regionais BR→AR, BR→CL e DE→NL; longas BR→DE, BR→JP e BR→US. **14 IPs de destino** (2 por país), **11 probes de origem** (Anchors do Brasil e da Alemanha) e **64 fluxos**. Dois destinos que ficaram 100% sem resposta (Tostado/AR e Nuremberg/DE) foram trocados por Buenos Aires e Mainz, com a versão anterior preservada. A classe não usa país nem categoria geográfica. |
| Período | 06/09/2026 04:32 UTC a 20/09/2026 04:32 UTC. Período A (baseline): 06/09 a 13/09. Período B (dataset): 13/09 a 20/09. Sem sobreposição. |
| Dentro do escopo | Leitura de medições existentes (`GET`); JSON bruto preservado; baseline congelado por fluxo; features relativas; rótulos OK / RISCO / FALHA; split temporal com folga e hold-out de fluxos; comparação com a classe majoritária e com a persistência; ficha da árvore e dicionário versionado. |
| Fora de escopo | Criar medições (`POST`) ou gastar créditos do RIPE Atlas. IPv6, traceroute e HTTP. Limiar global de RTT (50 ms, 100 ms ou qualquer outro). País, IP, rota ou `fluxo_id` como coluna da árvore. Balancear o dataset escolhendo rotas que "fabricam" uma classe. Preencher RTT ausente com 0. Split aleatório de linhas. Outros algoritmos (floresta, boosting, redes). O estado RECALIBRAR. |

---

## 5. Usuários e decisão apoiada

O alerta é para quem administra o enlace monitorado. Com **FALHA**, a ação é investigar perda, timeout ou desvio extremo. Com **RISCO**, a ação é observar e priorizar, sem tratar o evento como queda. Com **OK**, nenhuma intervenção. Uma mudança estável de patamar deveria levar a abrir um novo período de baseline (RECALIBRAR), e não a abrir chamado de falha; isso fica como trabalho futuro.

O mesmo contrato vale para um log local da instituição, depois de um aquecimento de pelo menos 1.500 amostras válidas naquele fluxo. Sem esse aquecimento não há mediana confiável e o modelo não opera.

---

## 6. Dados e fontes

| Fonte | O que fornece | Papel |
|---|---|---|
| RIPE Atlas v2, mesh de Anchors, ping IPv4 (`GET` público) | Timestamp, `probe_id`, destino, RTT da rajada (3 pacotes), enviados/recebidos | Medição bruta (`data/raw/`, 266 arquivos JSON, 178 MB) |
| Período A, por `fluxo_id` | Mediana, MAD, IQR, jitter típico, perda típica, proporção de resposta | Baseline congelado (`baseline_por_fluxo.csv`). Não é linha de treino. |
| Período B | Métricas relativas, janelas de 5 medições, classe e bloco | Dataset rotulado (`periodo_B_rotulado.csv`) |

**Volume observado:**
- **322.016 registros** na tabela de trabalho: 161.135 no Período A e 160.881 no B.
- **64 fluxos com baseline** (todos acima de 1.500 RTT válidos; nenhum excluído).
- **227 timeouts** (RTT vazio, nunca 0) e **0 duplicatas**.
- Cada fluxo tem entre 5.011 e 5.039 medições, de 5.040 esperadas.
- No Período B, a distribuição é **80,8% OK, 9,5% RISCO e 9,7% FALHA**. A malha passa a maior parte do tempo no próprio normal.

O alvo do preditor (classe 12 minutos à frente) não foi gravado como arquivo separado: ele é derivado no notebook (seção 5.4), buscando a medição do mesmo fluxo mais próxima de t + 720 s, no mesmo bloco.

Cadência do mesh: 240 segundos. O jitter é o desvio-padrão dos RTT da rajada só quando há pelo menos duas respostas; com 0 ou 1 resposta fica vazio (436 medições).

**Dicionário de dados:** versões v0.1 (bruto), v0.2 (ficha, métricas e classe), v0.3 (colunas relativas novas) e v0.4 (colunas da árvore final), todas no notebook. País, endereço e rota ficam só na auditoria (`config/tabela_desenho.csv`).

---

## 7. Custo dos erros

| Tipo de erro | O que significa | Consequência |
|---|---|---|
| Falso negativo de FALHA | Indisponibilidade ou desvio extremo classificado como OK ou RISCO | O enlace degrada sem investigação. **É o erro mais grave.** No teste: 4 de 3.657 FALHAs (2 viraram RISCO, 2 viraram OK). |
| Falso negativo de RISCO | Início de saturação tratado como OK | Atraso na priorização. RISCO é 9,5% do Período B. No teste: 0 casos. |
| Falso positivo de FALHA | Rota longa saudável, pico isolado ou mudança estável de caminho rotulados como queda | Fadiga de alerta e chamado indevido. No teste: 0 casos. |
| Falso positivo de RISCO | Oscilação normal do fluxo disparando alerta | Ruído operacional. A persistência (2 de 5 medições) corta o pico isolado. |

A métrica principal é o **F1 macro**, com recall de FALHA e a confusão RISCO↔FALHA reportados à parte. A acurácia isolada é enganosa com 80,8% de OK. O teste é usado uma vez.

---

## 8. Abordagem proposta

Um único modelo treinado com muitos fluxos, cada um descrito pelo desvio em relação ao próprio baseline ("modelo RTT normalizado").

Caminho seguido: ingestão do mesh (JSON bruto preservado) → Período A só para baseline → congelamento → métricas relativas no Período B → rótulo híbrido → corte temporal com folga e hold-out de fluxos → comparação com classe majoritária e persistência → árvore de decisão CART escolhida na validação → teste único → ficha da árvore.

### 8.1 O que a distância explica

O RTT bruto mistura o comprimento do caminho com o incidente. O que classifica é o comportamento do RTT **daquele** fluxo, junto com perda e jitter, sustentados no tempo.

Exemplos da nossa coleta que a árvore trata como OK quando estáveis:

| Caminho | RTT normal observado (mediana do Período A) | Leitura |
|---|---|---|
| DE→DE (Mainz) | 9,88 ms (fluxo `6372\|217.198.242.227`) | Normal baixo |
| BR→BR (Porto Alegre) | 11,9 a 23,3 ms (fluxos não vistos) | Normal do país |
| Regional (BR→AR, BR→CL, DE→NL) | mediana de 36,29 ms | Normal intermediário |
| BR→DE (Mainz) | 208,50 ms (fluxo `6410\|217.198.242.227`) | Normal transatlântico |
| BR→JP (Tsuchiura) | 271,6 a 305,8 ms (fluxos não vistos) | Normal do fluxo. Nos fluxos não vistos, 100% das medições OK continuaram OK. |

### 8.2 Baseline por fluxo

Uma ficha por `fluxo_id`, calculada só no Período A e congelada (o notebook confere que ela não muda numa nova execução).

| Passo | O que foi feito |
|---|---|
| 1 | Separar o fluxo e ordenar pelo timestamp. |
| 2 | Período A: 06/09/2026 04:32 até 13/09/2026 04:32 UTC. Período B: até 20/09/2026 04:32 UTC. Nenhum timestamp de um mesmo fluxo nos dois. |
| 3 | RTT válido = RTT presente. Timeout fica fora da mediana e do MAD, mas dentro do dataset como evento. |
| 4 | Piso de 1.500 RTT válidos no A. Resultado: os 64 fluxos passaram, todos com cerca de 2.500 RTT válidos. |
| 5 | Gravar `baseline_por_fluxo.csv` e congelar. |

| Campo da ficha | Fórmula (só Período A) |
|---|---|
| `mediana` | mediana dos RTT válidos |
| `MAD` | mediana(\|RTT − mediana\|) dos RTT válidos |
| `IQR` | Q3 − Q1 dos RTT válidos (usado só quando MAD = 0) |
| `jitter_tipico` | mediana do jitter nas medições com jitter presente |
| `perda_tipica` | mediana de `perda_pct`, inclusive timeout |
| `prop_resposta` | medições com RTT válido / medições do período |

Mediana por escopo (só auditoria): MAD de 0,08 ms nos curtos, 0,20 ms nos regionais e 0,87 ms nos longos. Nenhum fluxo teve MAD = 0 nem jitter típico = 0.

O escore robusto é a versão estável da regra dos três sigmas: `z_robusto = (RTT − mediana) / (1,4826 × MAD)`.

### 8.3 Features

Colunas da árvore final (dicionário v0.4):

| Coluna | Cálculo |
|---|---|
| `z_robusto` | (RTT − mediana) / (1,4826 × MAD); vazio sem RTT |
| `aumento_pct` | (RTT − mediana) / mediana × 100; vazio sem RTT |
| `jitter_relativo` | jitter / jitter típico; vazio sem jitter |
| `perda_pct` | (enviados − recebidos) / enviados × 100 |
| `timeout_atual` | 1 se não há RTT ou perda = 100% |
| `n5_timeout`, `n5_aumento80`, `n5_risco` | contagens nas últimas 5 medições do fluxo (persistência) |
| `z_tendencia` | z atual − média do z nas 3 medições anteriores (tendência) |
| `z_max5` | maior z nas últimas 5 |
| `n5_jitter3` | quantas das últimas 5 têm `jitter_relativo` ≥ 3 |
| `perda_media5` | média de `perda_pct` nas últimas 5 |

País, IP, rota, `fluxo_id`, timestamp e RTT absoluto ficam fora. RTT ausente fica vazio, com `timeout_atual = 1`.

### 8.4 Regra de rotulagem

Parar na primeira linha verdadeira. FALHA ganha de RISCO, e RISCO ganha de OK.

| Ordem | Classe | Condição | Medições no Período B |
|---|---|---|---|
| 1 | FALHA | `perda_pct` ≥ 10 | 236 |
| 2 | FALHA | `n5_timeout` ≥ 3 | 0 |
| 3 | FALHA | `z_robusto` ≥ 3,5 com RTT presente | 15.305 |
| 4 | FALHA | `n5_aumento80` ≥ 2 | 60 |
| 5 | RISCO | (2 ≤ z < 3,5, ou 30 ≤ aumento ≤ 80, ou jitter relativo ≥ 3) e `n5_risco` ≥ 2 | 15.249 |
| 6 | OK | nenhuma anterior (pico isolado também é OK) | 130.031 |

Casos especiais aplicados como na tabela do projeto (MAD = 0, jitter típico = 0, jitter vazio, RTT ausente); nenhum deles ocorreu nesta coleta, exceto RTT e jitter vazios.

**Mecanismo dominante:** 98% das FALHAs (15.305 de 15.601) vêm do desvio robusto. Como o MAD é de fração de milissegundo, variações pequenas já dão z ≥ 3,5. A regra 2 (timeout persistente) não disparou: só 227 timeouts em 322.016 medições, todos isolados.

### 8.5 Mudança de rota

O critério de RECALIBRAR (z alto, perda e jitter normais, por cerca de 1 hora) **não foi aplicado**. Uma troca estável de rota durante o Período B aparece hoje como FALHA pela regra 3. Isso está declarado nas limitações.

### 8.6 Como o modelo deve ser lido

A árvore não aprende que RTT alto é falha: com RTT e rota disponíveis, ela continuou escolhendo `z_robusto` na raiz e deu importância zero a eles. Para um fluxo nunca visto, o procedimento é de calibração: observar o período inicial, congelar a ficha e só então aplicar a árvore.

---

## 9. Avaliação

**Protocolo A — tempo.** Dentro do Período B, por fluxo e em ordem de tempo: treino 50% (13/09 04:32 → 16/09 16:32 UTC, 70.560 medições), validação 20% (→ 18/09 02:08, 27.953) e teste 30% (→ 20/09 04:32, 41.812). As 4 primeiras medições de cada fluxo na validação e no teste ficam numa **folga** (448 medições), para nenhuma janela de 5 usar o bloco anterior. Todos os blocos têm RISCO. Hiperparâmetros escolhidos só na validação; o teste foi aberto uma vez (07/10/2026 18:25 UTC, `teste_unico.json`).

**Protocolo B — fluxos novos.** Grupos inteiros de `fluxo_id`, separados antes de qualquer árvore: todos os fluxos para **Tsuchiura (BR→JP, longo)** e **Porto Alegre (BR→BR, curto)**, 8 fluxos e 20.108 medições. A escolha foi fixada pelo grupo (não sorteada) para garantir caminho curto e longo e o hold-out de BR→JP. A ficha de cada um vem só do Período A dele.

**Resultados:**

| Avaliação | F1 macro | Recall de FALHA | Observação |
|---|---|---|---|
| Validação (árvore T3 e T4) | 0,9998 | 0,9994 | Só 2 erros: FALHA → RISCO |
| Teste temporal (árvore final) | 0,9997 | 0,999 | Balanced accuracy 0,9996; matriz [[33.159, 0, 0], [0, 4.996, 0], [2, 2, 3.653]] |
| Classe majoritária ("sempre OK") no teste | 0,2949 | 0,000 | A árvore supera |
| Fluxos não vistos | 0,9997 | 0,999 | Longo estável: 100% OK mantidos; curto degradado: 100% marcado RISCO/FALHA |
| Preditor +12 min (árvore) | 0,5149 | 0,252 | — |
| Persistência ("repetir a classe atual") | 0,5409 | 0,400 | Supera a árvore: o entregável é um **detector** |

---

## 10. Riscos e limitações

- **Rótulos heurísticos.** A árvore aprende a política de rótulo (concordância de 99,99% no teste), não uma falha confirmada em log de roteador.
- **MAD muito pequeno.** Variações de fração de milissegundo disparam FALHA; o rótulo mede sensibilidade estatística, não necessariamente degradação percebida.
- **Jitter típico de cerca de 0,1 ms.** Rajadas de 3 pacotes estimam mal o jitter; 0,3 ms já marca o critério de RISCO.
- **Timeout persistente e perda são raros.** A regra 2 não disparou e só 236 medições têm perda ≥ 10%. O erro relevante do teste foi uma perda de 33% prevista como OK (`6349|103.202.216.76`, BR→JP, 19/09 03:03 UTC).
- **Baseline fixo** não acompanha deriva lenta nem troca de rota; RECALIBRAR não foi implementado.
- **Anchors não são a rede do campus.** Perda e jitter de último quilômetro ficam sub-representados.
- **Fluxos não independentes.** Os mesmos 11 probes de origem servem vários destinos; amostras a cada 4 minutos são autocorrelacionadas.
- **Lacunas na coleta.** 399 intervalos maiores que 360 s no Período B; as janelas de 5 contam linhas, não minutos.
- **Sete mais sete dias** cobrem um ciclo semanal em cada período, não a estabilidade entre semanas.
- **Dois destinos trocados.** Tostado e Nuremberg ficaram sem resposta nos 14 dias e foram substituídos; a versão anterior está preservada em `config/tabela_desenho_v1_descartada.csv`.

---

## 11. Critérios de sucesso

| # | Critério | Situação |
|---|---|---|
| 1 | Nenhum fluxo de teste contribui para o próprio baseline, e nenhuma feature usa país, IP ou rota | **Atendido.** Ficha só do Período A; colunas só relativas. |
| 2 | Detector com F1 macro acima da classe majoritária, recall de FALHA explícito | **Atendido.** 0,9997 contra 0,2949; recall de FALHA 0,999. |
| 3 | Preditor de 12 minutos supera a persistência | **Não atendido** (0,5149 contra 0,5409). A entrega se declara **detector**. |
| 4 | Fluxos novos: longo estável não colapsa em FALHA; curto degradado não colapsa em OK | **Atendido.** 100% e 100%. |
| 5 | Exemplos auditáveis | BR→JP estável como OK ✔; fluxo curto (DE→DE) como FALHA ✔; timeout persistente: não ocorreu nos dados; RECALIBRAR: não ativo. |
| 6 | Ficha e dicionário alinhados às colunas do modelo | **Atendido.** Ficha da árvore e dicionário v0.4 com as 12 colunas da árvore final. |

---

## 12. Alternativas consideradas

| Alternativa | Por que foi rejeitada |
|---|---|
| Limiar global de RTT (50/100 ms) | A classe vira distância: 77,4% das medições acima de 100 ms são OK no critério relativo. |
| Árvore com RTT absoluto e rota | Testada como contraste na Tarefa 3: aprendeu um corte fixo de 141,2 ms e caiu para F1 macro 0,557. Descartada. |
| Um modelo por fluxo | Caro em dados e manutenção; não serve para fluxos novos. |
| Média e desvio-padrão no baseline | Os picos que se quer detectar inflam a média e o desvio. Mediana e MAD preservam a escala (fator 1,4826). |
| Jitter e perda absolutos | Reintroduzem a distância; perda de 0,5% não é observável em 3 pacotes. |
| Preencher timeout com 0 ms | 0 ms parece latência excelente e polui a mediana. |
| Split aleatório de linhas | Janelas vizinhas do mesmo fluxo cairiam em treino e teste. Usamos corte temporal com folga. |
| Superamostrar rotas longas para "balancear" FALHA | Ensinaria o mapa; rota longa estável é justamente o OK que o modelo precisa ver. |
| Medições próprias no RIPE Atlas | Custam crédito e geram série curta. |

---

## 13. Perguntas em aberto

1. **RECALIBRAR.** Não entrou na re-rotulagem do Período B; o treino usou as três classes e o viés de mudança de rota está declarado. Fica para uma próxima versão.
2. **Limiares do rótulo** (z = 2 e 3,5; aumento de 30% e 80%; jitter relativo ≥ 3; perda ≥ 10%). Foram mantidos. Dado o MAD sub-milissegundo, vale avaliar na validação um piso para o denominador do z.
3. **Baseline móvel causal** substitui a ficha fixa quando houver série maior que 7 + 7 dias.
4. **Classificador.** Árvore de decisão CART (Gini, profundidade 5, 11 folhas, semente 42), escolhida na validação, como pede a disciplina.
5. **Preditor.** A 12 minutos o futuro ainda é, em grande parte, o estado atual; um horizonte diferente ou novas colunas de tendência podem ser testados.

---

## 14. Encadeamento

| Etapa | Produz | A etapa seguinte usa |
|---|---|---|
| Coleta (Tarefa 1) | `data/raw/` (JSON bruto), `config/` (`parametros.json`, `tabela_desenho.csv`), `bruto_tabela.csv`, dicionário v0.1 | Este bruto |
| Baseline e rótulo (Tarefa 2) | `baseline_por_fluxo.csv`, `periodo_B_rotulado.csv`, `corte_temporal.json`, dicionário v0.2 | Estes rótulos, estas métricas e este corte |
| Primeira árvore (Tarefa 3) | `arvore_T3.joblib`, `regras_T3.txt`, árvore de contraste descartada | Os erros da validação |
| Ajuste (Tarefa 4) | `arvore_T4.joblib`, tabela T3 → T4, dicionário v0.3 | Esta árvore |
| Árvore final (Tarefa 5) | `arvore_final.json`, `teste_unico.json`, ficha da árvore, dicionário v0.4 | — |

Não se rotula o período que estimou o baseline. Não se sorteia linha para o teste final.
