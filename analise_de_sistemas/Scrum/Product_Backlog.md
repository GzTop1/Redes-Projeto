# Product Backlog – Preditor de Falhas

**Projeto:** Preditor de Falhas em Rede · Grupo 7
**Product Owner:** Fernanda Akemi Martins Sanpei
**Atualizado em:** 22/10/2026

O Product Backlog é a lista **priorizada** de tudo o que o produto precisa ter. Quem decide a ordem é o Product Owner. Cada item é uma **história de usuário** no formato *Como [papel], quero [funcionalidade], para [benefício]*, com um **critério de aceite**: a condição que mostra que o item está pronto.

**Papéis usados nas histórias** (os mesmos atores do diagrama de casos de uso):
- **Administrador de Rede:** cadastra os fluxos e configura os parâmetros.
- **Analista de TI:** acompanha o painel, os alertas e o histórico.
- **Equipe do projeto:** precisa do item para construir, validar ou documentar o sistema.
- **Professores (avaliação):** precisam do item como evidência de entrega.

**Prioridade (MoSCoW):** **M** = obrigatório (*Must*) · **S** = importante (*Should*) · **C** = desejável (*Could*).
**Situação:** ✅ concluído · 🔄 em andamento · ⏳ a fazer · ❓ a confirmar com os professores.

---

## Histórias de usuário

| # | Prior. | História de usuário | Critério de aceite | Requisito | Sprint | Situação |
|---|:---:|---|---|---|---|:---:|
| PB01 | M | Como **equipe do projeto**, quero comparar um dataset público (CAIDA Ark) com a API do RIPE Atlas, para escolher a fonte de dados com justificativa. | Memorando de decisão entregue com as duas opções e a escolha justificada. | — | 1 | ✅ |
| PB02 | M | Como **equipe do projeto**, quero consumir uma medição pública da API do RIPE Atlas e salvar o JSON bruto, para validar a ingestão antes do projeto completo. | Notebook de ingestão com requisição válida, `DataFrame`, JSON salvo e metadados da coleta. | RF002 | 2 | ✅ |
| PB03 | M | Como **Administrador de Rede**, quero que o sistema monitore 30 destinos estratificados por continente e distância, para cobrir caminhos curtos, médios e longos sem viés de rota. | 30 âncoras e 150 fluxos registrados em `config/`. | RF001 | 3 | ✅ |
| PB04 | M | Como **Analista de TI**, quero que as medições de ping sejam coletadas e o JSON bruto preservado, para poder auditar e reprocessar os dados. | 420 arquivos JSON em `data/raw/`, coleta idempotente; RTT ausente nunca vira 0. | RF002, RF003 | 3 | ✅ |
| PB05 | M | Como **Analista de TI**, quero que cada fluxo tenha um baseline próprio calculado em uma semana de referência, para que a classe seja relativa ao normal daquele caminho. | `baseline_por_fluxo.csv` congelado, com P95/P99 de RTT e jitter e mínimo de 30 RTT válidos. | RF008 | 3 | ✅ |
| PB06 | M | Como **Analista de TI**, quero que cada medição seja classificada em OK, RISCO ou FALHA por uma regra clara, para saber quando agir. | Regra aplicada na ordem definida, com a condição que disparou cada classe registrada. | RF008 | 3 | ✅ |
| PB07 | M | Como **equipe do projeto**, quero 21 variáveis relativas ao baseline e um corte temporal com embargo, para treinar sem vazamento de informação. | `dataset_final.csv` e `corte_temporal.json` gravados; 13 fluxos separados antes do treino. | RF004 | 3 | ✅ |
| PB08 | M | Como **Analista de TI**, quero uma árvore de decisão com regras legíveis, para entender por que o sistema deu cada alerta. | Árvore escolhida só na validação; regras em português; matriz 3×3 e F1 macro. | RF004 | 3 e 4 | ✅ |
| PB09 | M | Como **equipe do projeto**, quero ajustar o modelo a partir dos erros da primeira árvore, para melhorar o desempenho de forma justificada. | Experimentos ligados a cada erro; grade de três famílias; tabela T3 → T4. | RF004 | 4 | ✅ |
| PB10 | M | Como **Analista de TI**, quero que o modelo final seja medido uma única vez em dados nunca vistos, para confiar no desempenho informado. | `teste_unico.json` gravado; comparação com persistência e classe majoritária; ficha do modelo. | RF004 | 4 | ✅ |
| PB11 | S | Como **professores (avaliação)**, queremos ver a árvore desenhada, as matrizes e a comparação árvore × Random Forest, para avaliar a legibilidade e a escolha do modelo. | Figuras em JPG em `modelos/figuras/`; árvore e Random Forest comparados no teste. | RF004 | 5 | ✅ |
| PB12 | M | Como **professores (avaliação)**, queremos os requisitos, os casos de uso e os diagramas UML do sistema, para avaliar a modelagem. | Documento UML com RF, RNF, casos de uso, classes, sequência e atividade (PDF/JPG). | Todos | 4 e 5 | ✅ |
| PB13 | M | Como **equipe do projeto**, quero as regras de negócio documentadas, para que todos usem os mesmos critérios de classificação e o mesmo contrato de dados. | Documento de regras de negócio publicado. | Todos | 5 | 🔄 |
| PB14 | M | Como **Analista de TI**, quero um painel que pingue 1 ou 2 IPs e classifique cada medição ao vivo, para acompanhar o estado da rede em tempo real. | Painel exibe OK/RISCO/FALHA por dispositivo a cada X segundos. | RF005 | 5 | ❓ |
| PB15 | M | Como **Analista de TI**, quero ver o histórico das últimas medições de cada dispositivo, para perceber tendências. | Gráfico ou lista com as últimas N medições e classes. | RF005 | 5 | ❓ |
| PB16 | M | Como **Analista de TI**, quero um botão para simular perda ou aumento de latência, para demonstrar a reação do modelo a RISCO e FALHA. | Evento injetado sob demanda, marcado como SIMULADO no painel. | RF006 | 5 | ❓ |
| PB17 | M | Como **equipe do projeto**, quero um `log_rede.csv` no formato do contrato de dados, para treinar e validar o modelo com dados de rede local. | 100 a 150 registros com as 3 classes; colunas do contrato. | RF002 | 4 e 5 | ❓ |
| PB18 | S | Como **equipe do projeto**, quero provocar cenários de falha (tráfego saturado, interface desligada, RTT alto), para garantir exemplos de RISCO e FALHA. | Cenários executados e descritos no documento de coleta. | RF006 | 4 e 5 | ❓ |
| PB19 | C | Como **equipe do projeto**, quero um gerador de dataset sintético e a comparação sintético × real, para testar o modelo antes do log real. | Script com regras documentadas e relatório de comparação. | RF004 | 5 | ❓ |
| PB20 | S | Como **Administrador de Rede**, quero configurar os parâmetros de medição (períodos, limiares, janelas), para adaptar o sistema a outra rede. | Parâmetros centralizados em `config/parametros.json`. | RF007 | 3 | ✅ |
| PB21 | M | Como **professores (avaliação)**, queremos o relatório consolidado, os slides e a apresentação, para avaliar o projeto completo. | Relatório e slides entregues; apresentação entre 10 e 12/11. | — | 6 | ⏳ |

## Ordem de prioridade atual (definida pelo PO)

Os itens concluídos saem do topo. A ordem do que falta é:

1. **PB13** – Regras de negócio, porque fecham a parte de documentação de Análise.
2. **PB17 e PB18** – `log_rede.csv` e cenários de falha, porque o retreino com dados de rede local depende deles.
3. **PB14, PB15 e PB16** – Painel ao vivo, histórico e simulação, a parte demonstrada na apresentação.
4. **PB19** – Gerador sintético e comparação, se os professores confirmarem que ainda vale.
5. **PB21** – Relatório consolidado, slides e ensaio.

> Os itens marcados com ❓ seguem a proposta oficial (ping na rede local). O grupo usou o RIPE Atlas no modelo; a necessidade desses itens está sendo confirmada com os professores. Se a resposta mudar o escopo, o PO reordena o backlog.
