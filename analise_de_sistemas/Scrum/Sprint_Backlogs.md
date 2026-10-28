# Sprint Backlogs – Preditor de Falhas

**Projeto:** Preditor de Falhas em Rede · Grupo 7
**Product Owner:** Fernanda Akemi Martins Sanpei
**Atualizado em:** 26/10/2026

O **Sprint Backlog** é o pedaço do Product Backlog que o time escolhe fazer em uma sprint, na Sprint Planning. Os períodos seguem o cronograma da proposta do projeto. Os itens vêm das entregas registradas no GitHub (commits, diários das Tarefas e `config/evidencias.jsonl`). Os códigos **PBxx** são os itens do [Product Backlog](Product_Backlog.md).

**Scrum Master:** rodou a cada sprint/tarefa, como a proposta permite: Isaac (Tarefa 1), Davi (Tarefa 2), Fernanda (Tarefa 3), Hendrick (Tarefa 4) e Geziel (Tarefa 5).

---

## Kickoff – 17 a 21/08/2026

**Meta:** formar a equipe, entender o contrato de dados e montar o backlog inicial.

| Item | Responsável | Situação |
|---|---|---|
| Formação da equipe e leitura da proposta | Todos | ✅ |
| Contrato de dados (`timestamp, ip, latencia_ms, perda_pacotes_pct, jitter_ms, status_real`) | Todos | ✅ |
| Backlog inicial | Todos | ✅ |

> O repositório começa em 08/09, então esta sprint não tem commits. O registro do kickoff depende das anotações do grupo.

## Sprint 1 – 24/08 a 04/09/2026

**Meta:** escolher a fonte de dados do projeto.

| Item | História | Responsável | Situação |
|---|---|---|---|
| Pesquisa do dataset CAIDA Ark × API do RIPE Atlas | PB01 | Isaac, Geziel, Fernanda, Hendrick, Davi | ✅ |
| Redação do memorando de decisão | PB01 | Isaac, Geziel, Fernanda, Hendrick, Davi | ✅ |

**Incremento:** memorando de decisão (entregue em 08/09).

## Sprint 2 – 07 a 18/09/2026

**Meta:** entregar o memorando e validar a ingestão de dados do RIPE Atlas.

| Item | História | Responsável | Situação |
|---|---|---|---|
| Entrega e correção do memorando (08 e 11/09) | PB01 | Fernanda, Isaac | ✅ |
| Notebook de ingestão: requisição, `DataFrame`, JSON e metadados (14 e 15/09) | PB02 | Isaac, Fernanda, Geziel, Hendrick | ✅ |
| Organização do repositório e das evidências (12 e 14/09) | — | Isaac, Fernanda | ✅ |

**Incremento:** `Coleta_de_dados.ipynb` e a primeira estrutura do repositório.

## Sprint 3 – 21/09 a 02/10/2026

**Meta:** coletar os dados do projeto, construir o baseline e rotular (Tarefas 1 e 2).

| Item | História | Responsável | Situação |
|---|---|---|---|
| Correção da coleta após o comentário da professora (26/09) | PB02 | Isaac | ✅ |
| 30 âncoras estratificadas e 150 fluxos (Tarefa 1) | PB03 | Isaac | ✅ |
| Coleta de 420 arquivos JSON nos Períodos A e B (Tarefa 1) | PB04 | Isaac | ✅ |
| Parâmetros em `config/parametros.json` (Tarefa 1) | PB20 | Isaac | ✅ |
| Baseline por fluxo só com o Período A (Tarefa 2) | PB05 | Davi | ✅ |
| Rotulagem OK/RISCO/FALHA e alvo t+1 (Tarefa 2) | PB06, PB07 | Davi | ✅ |
| Início da primeira árvore (Tarefa 3, a partir de 28/09) | PB08 | Fernanda | ✅ |

**Incremento:** dados brutos, `baseline_por_fluxo.csv` e `dataset_final.csv`. Tarefa 1 entregue em 01/10.

## Sprint 4 – 05 a 16/10/2026

**Meta:** treinar, ajustar e testar o modelo (Tarefas 3, 4 e 5) e documentar o sistema.

| Item | História | Responsável | Situação |
|---|---|---|---|
| Árvore CART, leitura do erro e árvore de contraste (Tarefa 3) | PB08 | Fernanda | ✅ |
| Experimentos e grade de três famílias; Random Forest escolhido (Tarefa 4) | PB09 | Hendrick | ✅ |
| Revisão do notebook contra o pipeline da professora (11/10) | PB03 a PB10 | Isaac | ✅ |
| Teste único, fluxos não vistos e ficha do modelo (Tarefa 5) | PB10 | Geziel | ✅ |
| Revisão dos diários e do RFC (13/10) | — | Fernanda, Davi | ✅ |
| Documento UML: requisitos, casos de uso e diagramas (13 e 14/10) | PB12 | Fernanda, Isaac | ✅ |
| Reorganização do GitHub por matéria (14/10) | — | Fernanda | ✅ |
| Definição do Product Owner (14/10) | — | Grupo (Fernanda) | ✅ |
| Modo "simular evento" do painel (previsto na proposta) | PB16 | — | ➡ Sprint 5 |

**Incremento:** modelo final (Random Forest, F1 macro de 0,7675 no teste), Tarefas 2 e 3 entregues (11 e 15/10) e documento UML.

## Sprint 5 – Integração – 19 a 30/10/2026 (em andamento)

**Meta:** incorporar o retorno das professoras, fechar a documentação e construir o aplicativo de monitoramento.

> Em 26/10 a Profa. Denise enviou o tutorial de Redes: o resultado para CC é um **aplicativo com dashboard** (histórico, perdas, tempos e status OK/RISCO/FALHA), testado nos cenários **normal, instável e indisponível**, e a entrega de Redes é um **vídeo**. O PO reordenou o backlog no mesmo dia.

| Item | História | Responsável | Situação |
|---|---|---|---|
| Gráficos, árvore desenhada e comparação árvore × Random Forest no teste, a partir do notebook didático da professora (20/10) | PB11 | Fernanda | ✅ |
| Revisão das Tarefas 1 a 5 e do RFC (20/10) | — | Fernanda | ✅ |
| Atualização do documento UML (20, 22 e 26/10), incluindo os relacionamentos e as visibilidades do diagrama de classes revisados pelo Isaac | PB12 | Fernanda, Isaac | ✅ |
| Regras de negócio, Product Backlog, Sprint Backlogs e registro das cerimônias (26/10) | PB13 | Fernanda (PO) | ✅ |
| Ajuste da documentação ao tutorial de Redes: backlog, UML (hosts locais e ping ICMP local) e pasta de Redes (26/10) | PB12, PB22, PB23 | Fernanda (PO) | ✅ |
| Entrega das Tarefas 4 e 5 (29/10) | PB09, PB10 | Grupo | 🔄 |
| Aplicativo com painel: ping a hosts locais, baseline do host, classificação ao vivo, histórico e alertas | PB14, PB15 | _a definir_ | ⏳ |
| Botão de simulação de falha (medição marcada como SIMULADA) | PB16 | _a definir_ | ⏳ |
| Histórico das medições no aplicativo (horário, host, métricas, classe atual e prevista) | PB17 | _a definir_ | ⏳ |
| Gerador sintético e comparação sintético × real | PB19 | — | ❌ não será feito |

## Sprint 6 – Redes e preparação final – 02 a 11/11/2026 (planejada)

**Meta:** testar o aplicativo nos três cenários, montar a rede no Packet Tracer, gravar e entregar o vídeo de Redes e preparar a apresentação.

| Item | História | Responsável | Situação |
|---|---|---|---|
| Testes nos cenários normal, instável (rede saturada, RTT alto) e indisponível (interface desligada), com a previsão × a ocorrência real registradas | PB18 | Todos | ⏳ |
| Rede local no Packet Tracer: topologia TCP/IP, protocolos por camada, ping entre os hosts e enlace derrubado | PB22 | _a definir_ | ⏳ |
| Coleta dos RGMs de todos para a capa do vídeo | PB23 | Fernanda | ⏳ |
| Roteiro do vídeo (introdução, objetivo, desenvolvimento, encerramento) | PB23 | _a definir_ | ⏳ |
| Gravação e edição (apresentador no canto da tela, 10 a 15 min), upload no YouTube como não listado — **meta: 08/11** | PB23 | Todos | ⏳ |
| **Entrega do link pelo Blackboard até 11/11/2026** (até 3 tentativas; vale a última) | PB23 | Fernanda (PO) | ⏳ |
| Relatório consolidado e slides | PB21 | _a definir_ | ⏳ |
| Ensaio da apresentação (testar o painel ao vivo) | PB21 | Todos | ⏳ |

**Apresentação:** 10 a 12/11/2026 · **Vídeo de Redes:** até 11/11/2026.
