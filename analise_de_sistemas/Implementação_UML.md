# Análise e Projeto de Sistemas – Diagramas UML

**Projeto:** Preditor de Falhas (Network Failure Predictor)

**Disciplina:** Análise e Projeto de Sistemas – 3N · Prof. Luís Ricardo

**Interdisciplinar com:** Profª Andrea Ono Sakai e Profª Denise Braito de Souza

**Curso:** Ciência da Computação – 4º semestre

**Equipe:** DSFSGAHAIB · **Período:** 15/09/2026 a 11/11/2026

**Product Owner:** Fernanda Akemi Martins Sanpei

| Integrantes |
|---|
| Davi Gabriel Borges dos Santos |
| Fernanda Akemi Martins Sanpei |
| Geziel de Andrade |
| Hendrick Ambriola |
| Isaac William Braz |

---

## Sumário

1. [Situação-problema](#1-situação-problema)
2. [Implementação dos diagramas UML](#2-implementação-dos-diagramas-uml)
3. [Etapa 1 – Requisitos](#3-etapa-1--requisitos-funcionais-e-não-funcionais)
4. [Etapa 2 – Diagrama de Casos de Uso](#4-etapa-2--diagrama-de-casos-de-uso)
5. [Etapa 3 – Diagrama de Classes](#5-etapa-3--diagrama-de-classes)
6. [Etapa 4 – Diagrama de Sequência](#6-etapa-4--diagrama-de-sequência)
7. [Etapa 5 – Diagrama de Atividade](#7-etapa-5--diagrama-de-atividade)
8. [Arquivos desta pasta](#8-arquivos-desta-pasta)

---

## 1. Situação-problema

Uma instituição de ensino deseja desenvolver um sistema web para auxiliar no gerenciamento de sua biblioteca. Atualmente, parte do controle do acervo e dos empréstimos é realizada de maneira manual, dificultando a consulta de informações e o acompanhamento da circulação dos livros.

O sistema deverá, inicialmente, contemplar funcionalidades como:

- cadastro de alunos;
- cadastro de livros;
- consulta ao acervo;
- registro de empréstimos;
- registro de devoluções;
- controle de atrasos;
- reserva de livros;
- consulta do histórico de empréstimos;
- relatórios administrativos.

## 2. Implementação dos diagramas UML

Os diagramas a seguir foram elaborados a partir do sistema realmente desenvolvido no projeto interdisciplinar (notebook de coleta, baseline, rotulagem e treinamento do modelo e painel de monitoramento). Todos foram produzidos em **PlantUML** e seguem a notação UML 2. Os códigos-fonte estão na pasta [`uml/`](uml/).

Por orientação da disciplina, os diagramas são entregues em **JPG** (pasta [`img/`](img/)) e reunidos em um único **PDF** ([`img/Diagramas_UML_Preditor_de_Falhas.pdf`](img/Diagramas_UML_Preditor_de_Falhas.pdf)).

## 3. Etapa 1 – Requisitos (Funcionais e Não Funcionais)

### 3.1 Requisitos Funcionais (RF)

Descrevem **o que** o sistema deve fazer.

| ID | Requisito | Descrição |
|---|---|---|
| RF001 | Cadastrar Fluxos e Hosts Monitorados | Registrar os hosts da rede local monitorados pelo aplicativo (IP ou nome, como o roteador, um servidor ou um site) e os pares sonda → âncora do RIPE Atlas (`probe_id`, `anchor_id` e `msm_id`) usados para treinar e testar o modelo. |
| RF002 | Coletar Dados de Telemetria (ICMP) | Enviar ping (ICMP Echo Request de 3 pacotes) a cada host local no intervalo configurado e registrar a resposta (Echo Reply: RTT mínimo, médio e máximo, pacotes enviados e recebidos, TTL); para os fluxos de treino, obter os mesmos dados na API pública do RIPE Atlas, a cada 240 s. |
| RF003 | Armazenar Histórico de Métricas | Guardar o JSON bruto da API e a tabela tratada (uma linha por fluxo e horário), incluindo perda e jitter calculados. |
| RF004 | Executar Algoritmo de Predição | Calcular as 21 variáveis relativas ao baseline e prever a classe da próxima medição com o modelo Random Forest (árvore de decisão mantida como versão interpretável, com o mesmo desempenho no teste). |
| RF005 | Visualizar Alertas e Histórico (Dashboard) | Exibir em painel o status OK/RISCO/FALHA de cada host, gráficos de latência, perda e jitter, alertas e histórico. |
| RF006 | Simular Eventos de Falha | Injetar perda de pacotes ou aumento de latência para demonstrar a reação do modelo, marcando a medição como SIMULADA. |
| RF007 | Configurar Parâmetros de Medição | Definir o período de baseline, os limiares de classificação (P95, P99 e perda), o tamanho das janelas, o intervalo entre pings e o tempo limite de resposta. |
| RF008 | Calcular Baseline e Rotular Medições | Calcular, para cada fluxo ou host, P95/P99 de RTT e jitter e TTL de referência (Período A para o RIPE Atlas; primeiros minutos de ping para um host local) e aplicar a regra de rotulagem OK/RISCO/FALHA. |

**Correspondência com o tutorial da Profa. Denise (Redes):**

| Requisito do tutorial | Requisito deste documento |
|---|---|
| RF01 – Cadastrar dispositivos/hosts monitorados | RF001 |
| RF02 – Executar verificações ICMP em intervalos definidos | RF002 e RF007 |
| RF03 – Registrar tempo de resposta e perda de pacotes | RF002 e RF003 |
| RF04 – Classificar o estado do host: normal, atenção ou falha | RF004 e RF008 (normal = OK, atenção = RISCO, falha = FALHA) |
| RF05 – Exibir histórico e gerar alertas | RF005 |

### 3.2 Requisitos Não Funcionais (RNF)

Descrevem **como** o sistema deve se comportar (qualidade, restrições e segurança).

| ID | Categoria | Descrição |
|---|---|---|
| RNF001 | Desempenho | Classificar uma nova medição (cálculo das variáveis + predição) em menos de 1 segundo, bem abaixo do intervalo entre medições. |
| RNF002 | Segurança | Enviar ping somente aos hosts cadastrados; acessar a API do RIPE Atlas somente com requisições GET de leitura em medições públicas, sem consumir créditos; qualquer chave de API fica em variável de ambiente, nunca no código ou no repositório. |
| RNF003 | Confiabilidade | Repetir uma requisição apenas em respostas 429 ou 5xx, com espera crescente entre tentativas; um host que não responde é registrado com perda de 100% sem travar o aplicativo, e a falha de um host ou fluxo não interrompe o monitoramento dos demais. |
| RNF004 | Integridade dos dados | Medição sem resposta é registrada com RTT ausente e perda de 100%, nunca como RTT = 0; o JSON bruto da API é preservado sem alteração. |
| RNF005 | Reprodutibilidade | Semente aleatória fixa (`SEED = 42`), versões das bibliotecas registradas em `requirements.txt` e períodos de coleta documentados permitem repetir o experimento. |
| RNF006 | Rastreabilidade | Cada classificação registra a regra que a disparou, cada medição indica a origem (REAL ou SIMULADA) e o modelo em uso é versionado. |
| RNF007 | Usabilidade | O painel usa cores fixas (verde = OK, amarelo = RISCO, vermelho = FALHA), identifica o host exibido e deixa explícito quando um dado é simulado. |
| RNF008 | Portabilidade | Executar em Python 3.11 (Windows, Linux ou Google Colab), com o painel acessível pelo navegador, sem instalação adicional para o usuário final. |
| RNF009 | Manutenibilidade | Código organizado em módulos (coleta, baseline/rotulagem, variáveis, modelo e painel), com os parâmetros centralizados em um único arquivo de configuração. |

## 4. Etapa 2 – Diagrama de Casos de Uso

### 4.1 Contexto do projeto

O Preditor de Falhas (Network Failure Predictor) é o projeto interdisciplinar que detecta sinais precoces de degradação e indisponibilidade em caminhos de rede. O aplicativo envia ping (ICMP Echo Request/Echo Reply) a hosts da rede local, registra latência, perda e jitter, compara cada medição com o baseline do próprio host e classifica o estado em OK, RISCO ou FALHA. O modelo foi treinado e testado com medições públicas de ping da plataforma RIPE Atlas, organizadas por fluxo (sonda → âncora); como as variáveis são relativas ao baseline, o mesmo modelo é aplicado aos hosts locais. Um modelo Random Forest prevê a classe da próxima medição, e uma árvore de decisão é mantida como versão interpretável: no teste, as duas ficaram praticamente empatadas (F1 macro de 0,7675 e 0,7673). Os resultados são apresentados em um painel de monitoramento.

**Conceitos e elementos:** o diagrama de casos de uso mostra o que o sistema oferece a cada ator, sem detalhar como é feito. Seus elementos são os **atores** (pessoas ou sistemas externos que interagem com o sistema), os **casos de uso** (elipses, cada uma uma funcionalidade) e a **fronteira do sistema** (retângulo).

**Relacionamentos:** **associação** (linha entre ator e caso de uso); **«include»** (comportamento obrigatório reutilizado – por exemplo, visualizar alertas sempre executa a predição); e **«extend»** (comportamento opcional – a simulação de falha estende a visualização de alertas).

### 4.2 Atores

| # | Ator | Tipo | Responsabilidade |
|---|---|---|---|
| 1 | Administrador de Rede | Principal | Cadastra os fluxos e configura os parâmetros de medição. |
| 2 | Analista de TI | Principal | Acompanha o painel, os alertas e o histórico e simula eventos de falha. |
| 3 | Host da rede local | Secundário (dispositivo) | Responde (ou não) aos pings ICMP do aplicativo: roteador, servidor, PC ou site monitorado. |
| 4 | API RIPE Atlas | Secundário (sistema externo) | Fornece os resultados das medições de ping usadas para treinar e testar o modelo. |

> O script coletor deixou de ser ator porque faz parte do próprio sistema.

### 4.3 Funcionalidades e relacionamento com os atores

| Ator | Caso de uso | Descrição | Relacionamentos |
|---|---|---|---|
| Administrador de Rede | UC01 – Cadastrar Fluxos e Hosts Monitorados | Define quais hosts da rede local o aplicativo monitora e quais pares sonda → âncora do RIPE Atlas fazem parte do escopo. | – |
| Administrador de Rede | UC07 – Configurar Parâmetros de Medição | Ajusta período de baseline, limiares (P95/P99 e perda), janelas e intervalo de consulta. | – |
| Analista de TI | UC05 – Visualizar Alertas e Histórico | Acompanha o status de cada host, os alertas e os gráficos. | inclui UC04 |
| Analista de TI | UC06 – Simular Eventos de Falha | Injeta perda ou aumento de latência para demonstrar o modelo. | inclui UC04, estende UC05 |
| Host da rede local | UC02 – Coletar Dados de Telemetria | O sistema envia ICMP Echo Request ao host e registra o Echo Reply (RTT, pacotes enviados/recebidos e TTL) no intervalo configurado. | inclui UC03 |
| API RIPE Atlas | UC02 – Coletar Dados de Telemetria | O sistema obtém os resultados de ping dos fluxos de treino a cada 240 s. | inclui UC03 |

**Casos de uso incluídos:** UC04 – Executar Algoritmo de Predição, que inclui UC08 – Calcular Baseline do Fluxo e UC03 – Armazenar Histórico de Métricas.

### 4.4 Diagrama

![Figura 1 – Diagrama de Casos de Uso do Preditor de Falhas](img/01_casos_uso.jpg)

*Figura 1 – Diagrama de Casos de Uso do Preditor de Falhas · código: [`uml/01_casos_uso.puml`](uml/01_casos_uso.puml)*

## 5. Etapa 3 – Diagrama de Classes

O diagrama de classes representa a estrutura estática do sistema: as classes, seus **atributos** (dados), seus **métodos** (operações) e as **associações** entre elas. Os símbolos `−` e `+` indicam visibilidade privada e pública.

**Principais classes:**

| Classe | Papel |
|---|---|
| `Fluxo` | Caminho monitorado: um par sonda → âncora do RIPE Atlas (`tipo = RIPE`, `id_fluxo = {probe_id}_{anchor_id}`) ou o computador do aplicativo → um host local (`tipo = LOCAL`); é composto por suas medições, seu baseline e seu histórico recente. |
| `Sonda` e `Ancora` | Pontos de origem e de destino do ping no RIPE Atlas (fluxos RIPE). |
| `HostLocal` | Dispositivo da rede local monitorado pelo aplicativo (fluxos LOCAL). |
| `Medicao` | Resultado de um ping de 3 pacotes – RTT mínimo, médio e máximo, perda, jitter, TTL e origem (REAL ou SIMULADA). |
| `Baseline` | Comportamento normal do fluxo no Período A (P95/P99 de RTT e jitter, TTL de referência); só é válido com pelo menos 30 RTT válidos. |
| `Rotulador` | Aplica a regra que transforma uma medição em OK, RISCO ou FALHA. |
| `HistoricoFluxo` e `ExtratorFeatures` | Guardam as últimas 12 medições e calculam as 21 variáveis relativas ao baseline (janelas de 3, 6 e 12 medições). |
| `Preditor` | Modelo treinado (Random Forest; a árvore de decisão é a alternativa interpretável) que prevê a classe da próxima medição, gerando uma `Previsao` e, quando necessário, um `Alerta`. |
| `ColetorICMPLocal`, `ColetorRIPE`, `SimuladorEventos` e `Dashboard` | Pingam os hosts locais, buscam as medições do RIPE Atlas, criam medições simuladas e coordenam a exibição no painel. |

**Relacionamentos (resumo):**

- **Composição** (losango cheio) – `Medicao`, `Baseline` e `HistoricoFluxo` só existem dentro de um `Fluxo`;
- **Agregação** (losango vazio) – o histórico referencia até 12 medições recentes (0..12);
- **Associação com multiplicidade** – 0..1, 1, 0..\*;
- **Dependência** (linha tracejada) – uma classe usa ou cria objetos de outra;
- **Enumerações** – `Classe` (OK, RISCO, FALHA), `Origem` (REAL, SIMULADA) e `TipoFluxo` (RIPE, LOCAL) para valores fixos.

![Figura 2 – Diagrama de Classes do Preditor de Falhas](img/02_classes.jpg)

*Figura 2 – Diagrama de Classes do Preditor de Falhas · código: [`uml/02_classes.puml`](uml/02_classes.puml)*

### 5.1 Tipos de relacionamento e multiplicidades

Cada linha abaixo corresponde a uma linha da Figura 2, agrupada pelo tipo de linha usado no diagrama.

**Composição** (linha sólida com losango cheio no lado do todo)

| Relacionamento | Multiplicidade | Significado |
|---|---|---|
| `Fluxo` – `Medicao` | 1 – 0..\* | Cada medição pertence a exatamente um fluxo, e um fluxo tem zero ou mais medições. Se o fluxo for removido, suas medições também deixam de existir. |
| `Fluxo` – `Baseline` | 1 – 1 | Cada fluxo tem exatamente um baseline, calculado no Período A. |
| `Fluxo` – `HistoricoFluxo` | 1 – 1 | Cada fluxo tem exatamente um histórico com as medições recentes. |

**Agregação** (linha sólida com losango vazio no lado do todo)

| Relacionamento | Multiplicidade | Significado |
|---|---|---|
| `HistoricoFluxo` – `Medicao` | – 0..12 | O histórico referencia de 0 a 12 medições recentes do fluxo. Quando uma medição sai da janela, ela continua existindo no fluxo. |

**Associações com multiplicidade** (linha sólida)

| Relacionamento | Multiplicidade | Significado |
|---|---|---|
| `Sonda` – `Fluxo` [origem] | 0..1 – 0..\* | Uma sonda pode ser a origem de vários fluxos; um fluxo RIPE tem uma sonda de origem, e um fluxo LOCAL não tem sonda. |
| `Ancora` – `Fluxo` [destino] | 0..1 – 0..\* | Uma âncora pode ser o destino de vários fluxos; só os fluxos RIPE têm âncora. |
| `HostLocal` – `Fluxo` [destino] | 0..1 – 0..\* | Um host local pode ser o destino de fluxos LOCAL; os fluxos RIPE não têm host local. |
| `Previsao` – `Alerta` [gera] | 1 – 0..1 | Uma previsão gera no máximo um alerta; previsões OK não geram alerta. |

**Associações navegáveis** (linha sólida com seta aberta)

| Relacionamento | Significado |
|---|---|
| `Dashboard` → `Preditor`, `ColetorICMPLocal`, `ColetorRIPE`, `SimuladorEventos`, `ExtratorFeatures` e `Rotulador` | O painel conhece esses componentes e os aciona para pingar, coletar, simular, calcular as variáveis, rotular e prever. |

**Dependências** (linha tracejada com seta)

| Relacionamento | Tipo | Significado |
|---|---|---|
| `Preditor` → `Previsao` | cria | O preditor gera uma nova previsão a cada medição classificada. |
| `ColetorICMPLocal` → `Medicao` | cria | O coletor envia o ICMP Echo Request ao host e cria a `Medicao` com origem REAL a partir do Echo Reply (ou com perda de 100% se não houver resposta). |
| `ColetorRIPE` → `Medicao` | cria | O coletor busca os resultados na API do RIPE Atlas e cria objetos `Medicao` com origem REAL. |
| `SimuladorEventos` → `Medicao` | cria | O simulador cria medições com origem SIMULADA. |
| `ExtratorFeatures` → `VetorFeatures` | cria | O extrator monta o vetor com as 21 variáveis. |
| `ExtratorFeatures` → `HistoricoFluxo` | usa | O extrator lê as últimas medições do histórico para calcular as janelas de 3, 6 e 12. |
| `Rotulador` → `Baseline` | usa | O rotulador compara a medição com o P95/P99 do baseline para definir OK, RISCO ou FALHA. |
| `Dashboard` → `Previsao` | exibe | O painel apenas mostra a previsão, sem guardá-la. |

### 5.2 Atributos e métodos com suas visibilidades

Como na Figura 2, o sinal `−` indica atributo **privado** e o sinal `+` indica método **público**.

| Classe | Atributos (privados) | Métodos (públicos) |
|---|---|---|
| `Fluxo` | `− id_fluxo : str`<br>`− tipo : TipoFluxo`<br>`− msm_id : int`<br>`− faixa_distancia : str` | `+ id() : str` |
| `Sonda` | `− id : int`<br>`− pais : str`<br>`− asn : int` | — |
| `Ancora` | `− id : int`<br>`− hostname : str`<br>`− ip_v4 : str`<br>`− pais : str`<br>`− asn : int` | — |
| `Medicao` | `− timestamp : int`<br>`− rtt_min : float`<br>`− rtt_avg : float`<br>`− rtt_max : float`<br>`− perda_pct : float`<br>`− jitter_ms : float`<br>`− ttl : int`<br>`− origem : Origem` | `+ rtt_ausente() : bool` |
| `Baseline` | `− n_rtt_validos : int`<br>`− mediana_rtt : float`<br>`− p95_rtt : float`<br>`− p99_rtt : float`<br>`− p95_jitter : float`<br>`− ttl_baseline : float`<br>`− status : str` | `+ calcular(medicoes_A) : Baseline`<br>`+ valido() : bool` |
| `HistoricoFluxo` | `− janela : deque<Medicao> [máx. 12]` | `+ adicionar(m : Medicao)`<br>`+ ultimas(n : int) : list` |
| `ExtratorFeatures` | — | `+ calcular(m, b, h) : VetorFeatures` |
| `VetorFeatures` | `− valores : float[21]` | — |
| `Rotulador` | — | `+ rotular(m : Medicao, b : Baseline) : Classe` |
| `Preditor` | `− versao : str`<br>`− familia : str` | `+ prever(v : VetorFeatures) : Classe` |
| `Previsao` | `− timestamp : int`<br>`− classe_atual : Classe`<br>`− classe_prevista : Classe`<br>`− origem : Origem` | — |
| `Alerta` | `− nivel : Classe`<br>`− mensagem : str` | — |
| `HostLocal` | `− ip : str`<br>`− nome : str` | — |
| `ColetorICMPLocal` | `− intervalo_s : int`<br>`− pacotes : int`<br>`− timeout_s : float` | `+ pingar(h : HostLocal) : Medicao` |
| `ColetorRIPE` | `− base_url : str` | `+ buscar(msm_id, probe_id, inicio, fim) : list<Medicao>` |
| `SimuladorEventos` | — | `+ injetar(tipo : str, intensidade : float) : Medicao` |
| `Dashboard` | — | `+ iniciar(f : Fluxo)`<br>`+ exibir(p : Previsao)`<br>`+ simular(tipo : str)` |

**Enumerações** (valores fixos): `TipoFluxo` = RIPE, LOCAL · `Origem` = REAL, SIMULADA · `Classe` = OK, RISCO, FALHA.

## 6. Etapa 4 – Diagrama de Sequência

O diagrama de sequência mostra a troca de mensagens entre objetos ao longo do tempo no cenário principal: o Analista de TI inicia o monitoramento de um host da rede local; o sistema monta o baseline do host (se ainda não houver) e, a cada intervalo, envia o ICMP Echo Request, recebe o Echo Reply (ou registra a falta de resposta), rotula, calcula as variáveis e prevê a classe da próxima medição.

**Elementos:** linhas de vida (ator e participantes), mensagens síncronas (seta cheia) e de retorno (seta tracejada), numeradas na ordem em que acontecem; fragmentos combinados **loop** (repetição a cada medição), **alt** (alternativa entre alerta de FALHA e atualização normal) e **opt** (simulação opcional acionada pelo analista).

![Figura 3 – Diagrama de Sequência: monitoramento e simulação](img/03_sequencia.jpg)

*Figura 3 – Diagrama de Sequência: monitoramento e simulação · código: [`uml/03_sequencia.puml`](uml/03_sequencia.puml)*

## 7. Etapa 5 – Diagrama de Atividade

O diagrama de atividade modela o fluxo de trabalho do monitoramento, com **raias** (*swimlanes*) que separam o que é feito pelo Analista de TI, pelo sistema e pelo host da rede local, que responde (ou não) ao ping. Elementos: nó inicial (círculo cheio), ações (retângulos arredondados), decisões (losangos), laço de repetição e nó final.

<p align="center">
  <img src="img/04_atividade_monitoramento.jpg" alt="Figura 4 – Diagrama de Atividade: monitoramento de um host" width="600">
</p>

*Figura 4 – Diagrama de Atividade: monitoramento de um host · código: [`uml/04_atividade_monitoramento.puml`](uml/04_atividade_monitoramento.puml)*

A Figura 5 detalha a ação **“Aplicar regra de rotulagem”**: as condições são verificadas em ordem e a primeira verdadeira define a classe da medição.

| Ordem | Condição | Classe |
|---|---|---|
| 1 | Perda ≥ 2 de 3 pacotes | FALHA |
| 2 | RTT > P99 do fluxo | FALHA |
| 3 | Perda = 1 de 3 pacotes | RISCO |
| 4 | RTT > P95 do fluxo | RISCO |
| 5 | Jitter > P95 do fluxo | RISCO |
| 6 | Nenhuma das anteriores | OK |

![Figura 5 – Diagrama de Atividade: regra de rotulagem OK/RISCO/FALHA](img/05_atividade_regra.jpg)

*Figura 5 – Diagrama de Atividade: regra de rotulagem OK/RISCO/FALHA · código: [`uml/05_atividade_regra.puml`](uml/05_atividade_regra.puml)*

## 8. Arquivos desta pasta

```
analise_de_sistemas/
├── Implementação_UML.md                          ← este documento
├── img/                               ← diagramas em JPG e todos juntos em PDF
│   ├── 01_casos_uso.jpg
│   ├── 02_classes.jpg
│   ├── 03_sequencia.jpg
│   ├── 04_atividade_monitoramento.jpg
│   ├── 05_atividade_regra.jpg
│   └── Diagramas_UML_Preditor_de_Falhas.pdf
└── uml/                               ← código-fonte PlantUML
    ├── 01_casos_uso.puml
    ├── 02_classes.puml
    ├── 03_sequencia.puml
    ├── 04_atividade_monitoramento.puml
    └── 05_atividade_regra.puml
```

Para editar um diagrama, altere o `.puml` e gere a imagem novamente em [plantuml.com/plantuml](https://www.plantuml.com/plantuml) ou com a extensão PlantUML do VS Code.
