# Documento de Regras de Negócio – Preditor de Falhas

**Projeto:** Preditor de Falhas em Rede (Network Failure Predictor) · Grupo 7
**Disciplina:** Análise e Projeto de Sistemas – Prof. Luís Ricardo (interdisciplinar com Estrutura de Dados II e Redes de Computadores)
**Product Owner:** Fernanda Akemi Martins Sanpei
**Fontes:** RFC do projeto, notebook `Projeto_Preditor_Falhas_PPF.ipynb` e proposta oficial do projeto interdisciplinar e tutorial de Redes da Profa. Denise (26/10)

---

## 1. Objetivo

Este documento reúne as regras que definem **como o sistema decide**: quais dados são aceitos, como cada medição é classificada em OK, RISCO ou FALHA, como a previsão é feita e avaliada e o que cada classe significa para quem opera a rede. As regras valem para o modelo, para o painel de monitoramento e para qualquer dado que entre no sistema, real ou simulado.

Cada regra tem um código (**RN001**, **RN002**…) para ser citada nos requisitos, nos casos de uso e no backlog.

## 2. Glossário

| Termo | Definição |
|---|---|
| **Fluxo** | Par sonda de origem → âncora de destino do RIPE Atlas. Identificador: `id_fluxo = {probe_id}_{anchor_id}` (exemplo: `6411_1070`). |
| **Medição (execução)** | Um ping de 3 pacotes de um fluxo, repetido a cada 240 s. |
| **RTT** | Tempo de ida e volta do pacote, em milissegundos. O sistema usa o RTT médio da execução. |
| **RTT ausente** | Execução sem nenhuma resposta (timeout). |
| **Perda** | Percentual de pacotes perdidos na execução: 0%, 33%, 67% ou 100%. |
| **Jitter** | Variação do RTT dentro da execução (desvio-padrão populacional dos RTT recebidos). |
| **Período A** | Semana de referência usada só para calcular o baseline: 21/09/2026 18:00 a 28/09/2026 18:00 UTC. |
| **Período B** | Semana seguinte, usada para rotular, treinar e testar: 28/09/2026 18:00 a 05/10/2026 18:00 UTC. |
| **Baseline** | Comportamento normal do fluxo, calculado no Período A. |
| **P95 / P99** | Valor abaixo do qual estão 95% / 99% das medições do fluxo no Período A. |
| **Persistência** | Previsão ingênua de que "a próxima medição terá a mesma classe da atual". É a principal comparação do modelo. |

## 3. Contrato de dados

### 3.1 Contrato oficial do projeto

A proposta interdisciplinar trava, antes de qualquer código, o formato dos dados de rede. **Todo conjunto de medições** usado pelo sistema deve ter exatamente estas colunas:

| Coluna | Tipo | Unidade | Descrição |
|---|---|---|---|
| `timestamp` | data e hora (UTC) | — | Momento da medição |
| `ip` | texto | — | Dispositivo ou destino monitorado |
| `latencia_ms` | decimal | ms | Latência (RTT) da medição |
| `perda_pacotes_pct` | decimal | % (0 a 100) | Percentual de pacotes perdidos |
| `jitter_ms` | decimal | ms | Variação da latência |
| `status_real` | texto | — | Classe da medição: `OK`, `RISCO` ou `FALHA` |

### 3.2 Correspondência com os dados do RIPE Atlas

O modelo foi treinado com a tabela de trabalho do RIPE Atlas. Cada coluna do contrato tem uma equivalente:

| Contrato oficial | Tabela de trabalho do projeto | Observação |
|---|---|---|
| `timestamp` | `timestamp` | Unix (segundos), UTC |
| `ip` | `id_fluxo` | O IP da âncora fica só em `config/tabela_desenho.csv`, para auditoria (ver RN016) |
| `latencia_ms` | `rtt_avg` | Também são guardados `rtt_min` e `rtt_max` |
| `perda_pacotes_pct` | `perda_pct` | Calculada pela RN005 |
| `jitter_ms` | `jitter_ms` | Calculado pela RN004 |
| `status_real` | `classe_atual` | Definida pela regra de rotulagem (RN011) |
| — | `ttl`, `sent`, `rcvd`, `n_rtt` | Campos extras que o contrato não exige |

### 3.3 Regras sobre os dados

| Código | Regra |
|---|---|
| **RN001** | A coleta usa **somente requisições `GET`** em medições públicas do RIPE Atlas. Não se criam medições (`POST`) nem se consomem créditos. Nenhuma chave de API é gravada no código ou no repositório. |
| **RN002** | O **JSON bruto** da API é guardado sem alteração. Toda tabela tratada é gerada a partir dele e pode ser refeita. |
| **RN003** | **RTT ausente é gravado vazio**, nunca como 0 ou −1. Um RTT 0 seria lido como "rede perfeita" e esconderia a falha. |
| **RN004** | **Jitter** = desvio-padrão populacional dos RTT recebidos na execução. Com 1 resposta, o jitter é 0; sem resposta, fica vazio. |
| **RN005** | **Perda** = (pacotes enviados − recebidos) ÷ enviados × 100, limitada entre 0 e 100. |
| **RN006** | Medições duplicadas (mesmo fluxo e mesmo `timestamp`) são removidas, mantendo uma. |
| **RN007** | Os períodos A e B começam em hora cheia UTC e **não se sobrepõem**. |
| **RN008** | O conjunto de medições deve conter as **3 classes** (OK, RISCO e FALHA). Um dataset sem uma delas não serve para treinar nem para avaliar. |

## 4. Regras do baseline

| Código | Regra |
|---|---|
| **RN009** | Um fluxo só entra em um período se tiver pelo menos **80% das execuções esperadas**: 2.016 das 2.520 de uma semana. No Período A, também precisa de pelo menos 30 TTL válidos. Só fluxos aprovados nos dois períodos seguem para o modelo; os excluídos são registrados com o motivo, e o destino **não** é trocado depois da coleta. |
| **RN010** | O baseline é calculado **só com o Período A** e fica **congelado**: P95 e P99 do RTT, P95 e P99 do jitter e mediana do TTL de cada fluxo. O baseline só é válido com **pelo menos 30 RTT válidos**. |
| **RN011** | Um **fluxo novo** só pode ser classificado depois de ter o próprio Período A, respeitando a RN009 e a RN010. Não se usa o baseline de outro fluxo. |
| **RN012** | Se 50% ou mais das medições de um fluxo no Período B ficarem acima do P99, o baseline é considerado **desatualizado** (provável mudança de rota) e o fluxo sai do dataset. |

## 5. Regras de classificação OK / RISCO / FALHA

### RN013 – Regra de rotulagem

Cada medição é comparada com o baseline **do próprio fluxo**. As condições são testadas **nesta ordem**, e a primeira verdadeira define a classe:

| Ordem | Condição | Classe |
|:---:|---|:---:|
| 1 | Perda ≥ 2 de 3 pacotes (≥ 67%) | 🔴 **FALHA** |
| 2 | RTT > P99 do fluxo | 🔴 **FALHA** |
| 3 | Perda ≥ 1 de 3 pacotes (≥ 33%) | 🟡 **RISCO** |
| 4 | RTT > P95 do fluxo | 🟡 **RISCO** |
| 5 | Jitter > P95 do fluxo | 🟡 **RISCO** |
| 6 | Nenhuma das anteriores | 🟢 **OK** |

| Código | Regra |
|---|---|
| **RN014** | **Não existe limiar global de RTT.** 200 ms é normal entre o Brasil e o Japão e péssimo entre duas cidades vizinhas. Por isso a classe é sempre relativa ao baseline do fluxo. |
| **RN015** | Toda classificação registra **qual condição da RN013 disparou**, para que qualquer rótulo possa ser auditado. |

## 6. Regras de predição

| Código | Regra |
|---|---|
| **RN016** | **Variáveis proibidas no modelo:** país, IP, rota, ASN, faixa de distância, `id_fluxo`, RTT absoluto e a própria classe atual. Esses dados existem só para auditoria. |
| **RN017** | O modelo usa só **variáveis relativas ao baseline** (razões ao P95/P99, perda, TTL) e **janelas do passado** do mesmo fluxo (últimas 3, 6 e 12 medições), num total de 21 variáveis. Nenhuma janela usa medições futuras. Quando o RTT está ausente, as variáveis que dependem dele recebem o valor sentinela −1, sem preencher com média ou mediana. |
| **RN018** | O **alvo** é a classe da **próxima medição** do fluxo (t+1, cerca de 4 minutos à frente). O par só é usado se o intervalo até a próxima medição for de no máximo 600 s. |
| **RN019** | A divisão entre treino, validação e teste é **temporal**, com **embargo de 60 minutos** entre os blocos. Não se sorteiam linhas para o teste. |
| **RN020** | **13 fluxos** (10%) são separados por sorteio (SEED 42) **antes de qualquer treino** e servem para testar o modelo em fluxos nunca vistos. |
| **RN021** | O modelo é escolhido **só pela validação**, com o maior **F1 macro**. Em caso de empate, vence o menor gap entre treino e validação e, depois, o modelo mais simples. A acurácia é reportada, mas não decide, porque 86% das medições são OK. |
| **RN022** | O **teste é aberto uma única vez**, e o resultado fica gravado em `teste_unico.json`. As execuções seguintes só leem esse arquivo. |
| **RN023** | O modelo só é aceito se superar a **classe majoritária** e a **persistência** no teste. O recall de FALHA é sempre informado. |

## 7. Regras de alerta e de uso

| Código | Regra |
|---|---|
| **RN024** | **Ação por classe:** 🔴 FALHA → investigar perda ou latência extrema; 🟡 RISCO → observar e priorizar; 🟢 OK → nenhuma ação. O alerta apoia a decisão de quem opera o enlace, mas **não é uma ordem de intervenção**. |
| **RN025** | O painel usa **cores fixas**: verde = OK, amarelo = RISCO, vermelho = FALHA. Cada status exibido indica a qual fluxo ou dispositivo se refere. |
| **RN026** | Toda medição **simulada** (evento injetado pelo botão "simular evento") é marcada como **SIMULADA** e exibida de forma diferente da medição real. Medições simuladas **nunca** entram no treino, no baseline nem no histórico real. |
| **RN027** | O sistema registra a **origem** de cada medição (REAL ou SIMULADA) e a **versão do modelo** usada em cada previsão. |

## 8. Regras do monitoramento na rede local (aplicativo)

Regras acrescentadas em 26/10 a partir do tutorial de Redes da Profa. Denise, que define o aplicativo de monitoramento por ICMP de hosts da rede local.

| Código | Regra |
|---|---|
| **RN028** | O aplicativo envia ping **somente aos hosts cadastrados** (RF001). Cada verificação é um **ICMP Echo Request de 3 pacotes**, com tempo limite configurável. Um host que não responde gera uma medição com **perda de 100% e RTT vazio** (RN003), sem travar o monitoramento dos outros hosts. |
| **RN029** | **Baseline do host local:** antes de prever, o aplicativo pinga o host até ter **pelo menos 30 RTT válidos** e calcula P95 e P99 do RTT e do jitter (equivalente local da RN010). Enquanto o baseline não está pronto, o painel mostra as métricas com o aviso "montando baseline", sem previsão. Não se usa o baseline de outro host (RN011). |
| **RN030** | O aplicativo guarda o **histórico de cada medição** com as colunas do contrato (seção 3.1) – `ip` = IP do host, `latencia_ms` = RTT médio da verificação e `status_real` = classe da medição pela RN013 – e a classe prevista para a medição seguinte. Medições simuladas ficam marcadas e não entram no baseline (RN026). |
| **RN031** | O intervalo entre pings é configurável (RF007). Como as janelas contam **medições** (3, 6 e 12) e não minutos, o tempo coberto por elas depende do intervalo escolhido; o intervalo usado nos testes é registrado junto com o histórico. |
| **RN032** | **Testes obrigatórios** em três cenários: **normal**, **instável** (rede saturada ou latência alta) e **indisponível** (interface desligada ou host fora do ar). Em cada um, a classe prevista é comparada com a classe da medição seguinte (ocorrência real) e com o resultado do mesmo cenário no Cisco Packet Tracer. |

## 9. Rastreabilidade

| Regra | Requisitos funcionais | Casos de uso |
|---|---|---|
| RN001 a RN008 | RF002 Coletar dados de telemetria · RF003 Armazenar histórico | UC02, UC03 |
| RN009 a RN012 | RF001 Cadastrar fluxos e hosts · RF007 Configurar parâmetros · RF008 Calcular baseline e rotular | UC01, UC07, UC08 |
| RN013 a RN015 | RF008 Calcular baseline e rotular | UC08 |
| RN016 a RN023 | RF004 Executar algoritmo de predição | UC04 |
| RN024 a RN025 | RF005 Visualizar alertas e histórico | UC05 |
| RN026 a RN027 | RF006 Simular eventos de falha | UC06 |
| RN028 a RN032 | RF001 Cadastrar fluxos e hosts · RF002 Coletar telemetria ICMP · RF003 Armazenar histórico · RF007 Configurar parâmetros · RF008 Calcular baseline | UC01, UC02, UC03, UC07, UC08 |

Os requisitos e os casos de uso estão no documento UML de Análise de Sistemas (`analise_de_sistemas/`).
