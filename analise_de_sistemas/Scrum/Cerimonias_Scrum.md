# Registro das Cerimônias Scrum – Preditor de Falhas

**Projeto:** Preditor de Falhas em Rede · Grupo 7
**Product Owner:** Fernanda Akemi Martins Sanpei
**Atualizado em:** 26/10/2026

O Scrum tem quatro cerimônias em cada sprint:
- **Sprint Planning** (início): o time escolhe o que vai fazer.
- **Daily Scrum** (todo dia, até 15 min): cada um conta o que fez, o que vai fazer e o que está travando.
- **Sprint Review** (fim): o incremento pronto é mostrado ao PO e aos professores, que dão feedback.
- **Sprint Retrospective** (fim): o time avalia o próprio jeito de trabalhar.

> **Como este registro foi montado:** a partir das evidências que estão no GitHub: os commits, os prints da pasta `prints/` (incluindo o **histórico de revisões do Colab**, que mostra quem editou o notebook e quando) e os registros com data e hora dos arquivos `evidencias.jsonl`. Nada aqui foi escrito sem uma evidência correspondente.

---

## 1. Sprint Planning

| Sprint | Data de início | Meta definida | Itens escolhidos (Product Backlog) | Scrum Master |
|---|---|---|---|---|
| Kickoff | 17/08 | Formar a equipe e entender o contrato de dados | Backlog inicial | — |
| Sprint 1 | 24/08 | Escolher a fonte de dados | PB01 | — |
| Sprint 2 | 07/09 | Entregar o memorando e validar a ingestão | PB01, PB02 | — |
| Sprint 3 | 21/09 | Coletar, fazer o baseline e rotular (Tarefas 1 e 2) | PB03 a PB07, PB20 | Isaac (T1), Davi (T2) |
| Sprint 4 | 05/10 | Treinar, ajustar e testar o modelo (Tarefas 3 a 5); documentar o sistema | PB08 a PB10, PB12 | Fernanda (T3), Hendrick (T4), Geziel (T5) |
| Sprint 5 | 19/10 | Incorporar o retorno das professoras, fechar a documentação e construir o aplicativo de monitoramento | PB11 a PB17 | Geziel (T5) |
| Sprint 6 | 02/11 | Testes nos 3 cenários, Packet Tracer, vídeo de Redes (até 11/11), relatório, slides e ensaio | PB18, PB21 a PB23 | _(definir)_ |

O **contrato** de cada Tarefa (seção "Contrato desta tarefa" dos diários) registra o que foi combinado em cada planning: o que **entra** (vindo da tarefa anterior), o que **sai** (para a próxima) e o que **não sai** dela.

## 2. Daily Scrum (assíncrona)

**Formato:** a daily do grupo foi **assíncrona**. Cada integrante registrava o que fez **no próprio trabalho**: no histórico de revisões do Colab (versões nomeadas), nos commits do GitHub e no registro `evidencias.jsonl`, que o notebook grava com data e hora a cada etapa concluída. O grupo de mensagens era usado para combinar o próximo passo e avisar impedimentos.

As três perguntas da daily, respondidas a partir dessas evidências:

| Data | Integrante | O que fez | Próximo passo | Impedimento | Evidência |
|---|---|---|---|---|---|
| 08/09 | Todos | Cada um escreveu uma seção do memorando de decisão (CAIDA Ark × RIPE Atlas); memorando publicado no GitHub | Corrigir a pesquisa e os links | — | `prints/*/Entrega_1/`; commit "Estrutura de dados II - entrega 1" |
| 11/09 | Fernanda | Corrigiu a pesquisa, os links e o caminho das evidências do memorando | Montar o notebook de ingestão | — | commits "Correção pesquisa", "Correção dos links" |
| 12/09 | Isaac | Organizou o repositório e as próprias evidências | Notebook de ingestão | — | commit "organizando o repositório e evidencias do isaac" |
| 14/09 | Fernanda | Organizou as pastas de prints, subiu as evidências da Entrega 2 e o `Coleta_de_dados.ipynb` | Revisar o notebook de coleta | — | commits de 14/09; `prints/*/Entrega_2/` |
| 15/09 | Fernanda, Isaac | Fernanda atualizou o notebook de coleta; Isaac corrigiu os links das evidências de contribuição | Coleta oficial | — | commits de 15/09 |
| 25/09 | Isaac | Fez a coleta oficial da medição 1001 e subiu os metadados | Aguardar retorno da professora | — | commit "Adiciona metadados da coleta oficial (medição 1001, 25/09/2026)" |
| 26/09 | Isaac | Corrigiu o notebook de coleta | Começar a Tarefa 1 | Comentário da professora Andréa sobre a coleta | commit "Correção depois do comentário da professora Andrea" |
| 30/09 | Fernanda | Organizou as evidências da Entrega 2 de Geziel e Hendrick | Tarefa 1 | — | commits de 30/09 |
| 04/10 | Isaac | Fixou três versões da Tarefa 1 no Colab (21:28, 21:36 e 22h) | Fechar a coleta | — | histórico de revisões do Colab nos prints `Adição_T2` a `Adição_T5` |
| 05/10 | Isaac | Nova versão no Colab (20h) e prints da Tarefa 1 no GitHub | Passar a coleta para a Tarefa 2 | — | Colab; commit "Print das evidências referente a Tarefa1" |
| 06/10 | Fernanda | Subiu o notebook de coleta atualizado e o print 5 | Tarefa 3 | — | commit "Coleta de dados atualizado \| 05/10" |
| 07/10 | Davi | Tarefa 2 no Colab (versões das 11:22 e 14:06, edição às 14:11): inspeção do bruto, ficha de baseline, rotulagem e corte temporal | Passar o dataset rotulado para a Tarefa 3 | — | `prints/Davi/Tarefa_1/Adição_T2`; prints T2_2.1 a T2_2.5; commit "Adicionando evidências T2" |
| 07/10 | Fernanda | Tarefa 3 no Colab (14:17): primeira árvore, matriz e árvore de contraste; prints no GitHub | Passar a árvore para a Tarefa 4 | — | `prints/Fernanda/Tarefa_1/Adição_T3`; prints T3_3.2 a T3_3.4; commit "evidencia Tarefa 3" |
| 07/10 | Hendrick | Tarefa 4 no Colab (14:23): diagnóstico do erro da T3, experimentos e comparação T3 → T4 | Passar o modelo ajustado para a Tarefa 5 | — | `prints/Hendrick/Tarefa_1/Adição_T4`; prints T4_4.1 a T4_4.3; commit de 07/10 |
| 07/10 | Geziel | Tarefa 5 no Colab (14h): modelo congelado, teste único, fluxos não vistos, ficha | Revisar com o grupo | Resultados bons demais (F1 macro de 0,9998 na validação e 0,9997 no teste) | `prints/Geziel/Tarefa_1/Adição_T5`; prints T5_5.1 a T5_5.5; `evidencias.jsonl` |
| 08/10 | Fernanda | Subiu o notebook PPF e atualizou o diário da Tarefa 1 e o checklist | Revisão do notebook | — | commits "Adicionando PPF" |
| 11/10 | Isaac | Refez o notebook seguindo o modelo da professora (correções C01 a C16), rodou de novo as Tarefas 1 a 5 e o teste de equivalência (123 de 123 idênticos); reorganizou os prints em "Tarefa 1 antiga" e "Tarefa 1 correções" | Revisar diários e RFC | Primeira versão divergia do modelo da professora | `config/evidencias.jsonl` (11/10, 01h a 15h UTC); `prints/Isaac/Tarefa_1/Tarefa 1 correções/` |
| 13/10 | Fernanda, Davi, Geziel | Revisão do RFC e dos diários das Tarefas 1 a 5; PPF revisado no GitHub | Documentação de Análise | — | commits "Revisão tarefa2" (Davi), "Revisão tarefa 5" (conta GzTop1), "Revisão RFC" |
| 14/10 | Fernanda | Criou a pasta de Análise de Sistemas com o documento UML; reorganizou o GitHub por matéria | Retorno da professora | — | commits de 14/10 |
| 20/10 | Fernanda | Incorporou o notebook didático da professora (gráficos, árvore desenhada, árvore × Random Forest no teste); revisou Tarefas 1 a 5, RFC e UML | Atualizar o UML | — | `config/evidencias.jsonl` (20/10 15:19 UTC); commits de 20/10 |
| 22/10 | Fernanda | Revisou o UML (diagramas `.puml` e imagens) | Documentos Scrum e regras de negócio | — | commits de 22/10 |
| 26/10 | Isaac, Fernanda | Isaac refez a seção do diagrama de classes (relacionamentos e visibilidades) da Fase 2; Fernanda subiu os documentos de Scrum e, com o tutorial da Profa. Denise, reordenou o backlog e ajustou o UML e a pasta de Redes | Aplicativo com painel e Packet Tracer | Escopo de Redes mudou: entrega passa a ser um vídeo e o painel deixa de ser opcional | Documento da Fase 2; commits de 26/10; tutorial da Profa. Denise |

**Impedimentos registrados e como foram resolvidos:**

| Quando | Impedimento | Como foi resolvido |
|---|---|---|
| 26/09 | Comentário da professora Andréa sobre o notebook de coleta | Isaac corrigiu o notebook no mesmo dia |
| 07/10 | F1 macro de 0,9998 na validação: resultado bom demais, sinal de vazamento (a árvore usava a classe da própria medição) | Na revisão de 11/10 o alvo virou a classe da **próxima** medição (C01 e C12), e o F1 macro passou a 0,77, um valor realista |
| 07/10 | Destinos que não respondiam (Tostado e Nuremberg) foram trocados depois da coleta | Substituído pela regra de cobertura mínima de 80%, decidida antes e igual para todos (C08) |
| 11/10 | A primeira versão do pipeline (z-robusto, mediana/MAD, horizonte de 12 min) divergia do modelo da professora | Pipeline refeito com as correções C01 a C16 e teste de equivalência (123 de 123) |
| 11/10 | Regras da API do RIPE Atlas: repetição em erro 404 e janelas desalinhadas | Repetição só em 429/5xx, cache de 24 h e períodos em hora cheia UTC (C05 e C06) |
| 20/10 | Erro 400 da API ao rodar a Tarefa 1 de novo | A Tarefa 1 não precisa ser rodada de novo; o roteiro de execução parte da Tarefa 2 |
| 26/10 | Tutorial de Redes mudou o escopo: aplicativo com dashboard obrigatório e entrega de Redes em vídeo até 11/11 | O PO reordenou o backlog no mesmo dia (PB14 a PB18, PB22 e PB23) e descartou o gerador sintético (PB19) |

## 3. Sprint Review

| Sprint | Data | Incremento apresentado | Retorno recebido / ação |
|---|---|---|---|
| Sprint 1 → 2 | 08/09 | Memorando de decisão (CAIDA Ark × RIPE Atlas) | Pesquisa e links corrigidos em 11/09 |
| Sprint 2 → 3 | 15 a 26/09 | Notebook de ingestão do RIPE Atlas | Comentário da professora Andréa; correção em 26/09 |
| Sprint 3 | 01/10 | Tarefa 1 – coleta bruta | Revisada contra o modelo da professora em 11/10 (C01 a C08) |
| Sprint 4 | 11/10 | Tarefa 2 – baseline e rotulagem | Entregue já com as correções C09 a C11 |
| Sprint 4 | 15/10 | Tarefa 3 – primeira árvore | Entregue com a grade e o desempate da professora (C12) |
| Sprint 5 | 20/10 | Tarefas 3 e 4 no GitHub (revisão com a docente) | A professora enviou o notebook didático de árvore e Random Forest; o grupo acrescentou gráficos, árvore desenhada e comparação árvore × Random Forest no teste, sem mudar o modelo |
| Sprint 5 | 29/10 | Tarefas 4 e 5 – modelo final e teste único | _(registrar o retorno após a entrega)_ |
| Sprint 6 | 11/11 | Vídeo de Redes (Blackboard) | _(registrar após a entrega)_ |
| Sprint 6 | 10 a 12/11 | Apresentação final | _(registrar após a apresentação)_ |

## 4. Sprint Retrospective

Tirada das colunas "Dificuldades" e "O que pretendo manter/ajustar" dos diários das Tarefas.

| Sprint / Tarefa | O que funcionou | O que não funcionou | O que vamos manter ou ajustar |
|---|---|---|---|
| Sprint 3 – Tarefa 1 (Isaac) | Coleta idempotente e registro de evidências com data e hora | Ajuste fino das regras da API e das janelas em hora cheia UTC | Manter a equivalência com o código da professora e o rastreio em `evidencias.jsonl` |
| Sprint 3 – Tarefa 2 (Davi) | Ficha de baseline congelada e conferida à mão | Garantir que nenhuma janela usasse medições do bloco seguinte | Manter a ficha congelada e o corte único para as Tarefas 3 a 5 |
| Sprint 4 – Tarefa 3 (Fernanda) | Só variáveis relativas; árvore de contraste mostrou o atalho da distância | O erro se concentra nas transições: a árvore mantém a classe e quase não antecipa mudanças | Manter o teste fechado; levar a confusão RISCO → OK para a Tarefa 4 |
| Sprint 4 – Tarefa 4 (Hendrick) | Cada experimento ligado a um erro da Tarefa 3 | Nenhuma mudança na árvore trouxe ganho; o Random Forest ganhou só +0,0011 | Manter a escolha só pela validação e apresentar o que foi descartado |
| Sprint 4 – Tarefa 5 (Geziel) | Teste aberto uma única vez, com trava no notebook | Modelo antecipa pouco os inícios de FALHA | Declarar as limitações com clareza e manter a ficha alinhada às variáveis |
| Sprint 5 – Grupo | Retorno da professora incorporado em um dia, sem refazer o modelo | Trabalho concentrado em um responsável por tarefa; PO formalizado só na Sprint 4; a primeira versão das Tarefas 2 a 5 foi feita toda em 07/10 e só depois revisada | Desconfiar de resultado bom demais; dividir os itens de Redes e do painel com responsável e data no Kanban |

## 5. Quadro Kanban

O quadro do projeto fica no GitHub Projects (colunas *Todo*, *In Progress* e *Done*): https://github.com/users/GzTop1/projects/1
