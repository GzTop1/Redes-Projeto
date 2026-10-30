# Preditor de Falhas na Rede – Grupo 7

Projeto interdisciplinar que usa medições públicas de ping do **RIPE Atlas** para classificar cada medição de um caminho da internet em **OK**, **RISCO** ou **FALHA** e prever a classe da **próxima** medição.

Centro Universitário Braz Cubas · Ciência da Computação · 4º semestre · 2º semestre de 2026

## Mostra de Tecnologia

| Item | Link |
|---|---|
| Página do projeto (artigo) |  https://akemiizinh4.github.io/Site_PreditorDeFalhas/ |
| Vídeo pitch (90 s) | _a publicar_ |

## O problema

Redes raramente caem de uma vez. Antes da queda, a latência sobe e alguns pacotes começam a se perder. A pergunta do projeto é se esses sinais são suficientes para antecipar a próxima medição.

A dificuldade é que **não existe um limite de latência que sirva para todos os caminhos**. Um caminho curto normal fica em 1 ms; um intercontinental normal fica em 300 ms. Um limite fixo mediria distância, não problema.

A solução foi dar a cada caminho o seu próprio normal:

1. **Período A** (21 a 28/09/2026) — o sistema observa cada fluxo por sete dias e congela o normal dele: a mediana, o P95 e o P99 do RTT e do jitter.
2. **Período B** (28/09 a 05/10/2026) — cada medição é comparada com o normal **do próprio fluxo**, em forma de razão. O modelo nunca vê RTT absoluto, nem país, nem IP, nem distância.

## Como funciona

- **Dados:** 131 fluxos `sonda → âncora` do RIPE Atlas, ping de 3 pacotes ICMP a cada ~240 s, coletados pela API REST pública (somente `GET`).
- **Rótulo:** para em cada medição na primeira regra verdadeira — perda ≥ 2/3 → FALHA; RTT > P99 → FALHA; perda ≥ 1/3 → RISCO; RTT > P95 → RISCO; jitter > P95 → RISCO; senão OK.
- **Alvo:** a classe da **próxima** medição (t+1), só para pares com intervalo de até 600 s.
- **Variáveis:** 21, todas relativas ao baseline do fluxo, em janelas de 3, 6 e 12 medições. Valor ausente vira −1 (sentinela), sem imputar média.
- **Separação:** corte temporal com embargo de 60 min — treino nos dias 0–5 do Período B, validação no dia 5–6, teste no dia 6–7. Além disso, 13 fluxos ficaram **inteiramente fora** do treino.
- **Modelos:** 58 comparados (30 árvores de decisão, 24 florestas aleatórias e 4 Naive Bayes), escolhidos pelo macro-F1 na validação.
- **Teste:** aberto **uma única vez**, em 11/10/2026 14:35:52 UTC, e registrado em `teste_unico.json`.

## Resultados

Teste final com 40.453 medições:

| Modelo | macro-F1 |
|---|---|
| **Random Forest (escolhido)** | **0,7675** |
| Árvore de decisão | 0,7673 |
| Persistência (repetir a classe atual) | 0,7302 |
| Sempre OK | 0,3082 |

Na classe FALHA: precisão 0,8240 e recall 0,6597 — ou seja, o modelo encontra cerca de duas em cada três falhas, e quando ele avisa, costuma estar certo. Nos 13 fluxos nunca vistos no treino o desempenho se manteve (0,6275 contra 0,6207 da persistência), o que indica que ele aprendeu o padrão e não decorou os caminhos.

**Limitação conhecida e medida:** o modelo é um detector suavizado. Ele acerta a continuação de uma falha, mas antecipa pouco o **primeiro instante** dela — recall de 0,0195 nos 411 inícios de falha do teste. Isso está documentado e é o próximo passo do projeto.

## Organização do repositório

| Matéria | Professor(a) | Pasta |
|---|---|---|
| Estrutura de Dados II | Profª Andréa Ono Sakai | [Estrutura_de_Dados_II](Estrutura_de_Dados_II/) |
| Redes de Computadores | Profª Denise Braito de Souza | [Redes_de_Computadores](Redes_de_Computadores/) |
| Análise e Projeto de Sistemas | Prof. Luís Ricardo | [analise_de_sistemas](analise_de_sistemas/) |

Dentro de **Estrutura de Dados II**:

| Pasta | O que tem |
|---|---|
| `Entrega_1_Memorando/` | Memorando de decisão: por que RIPE Atlas e não CAIDA Ark |
| `Entrega_2_Coleta/` | Notebook de ingestão da API e metadados das coletas |
| `Projeto_Preditor_Redes_Grupo7/` | Notebook do projeto, as cinco tarefas documentadas, o RFC e os artefatos congelados |

As evidências individuais de cada integrante estão em [prints](prints/), separadas por pessoa e por entrega.

## Reproduzir

O notebook `Projeto_Preditor_Redes_Grupo7/Projeto_Preditor_Falhas_PPF.ipynb` roda de ponta a ponta no Google Colab. Ele é idempotente: refaz só o que falta, guarda as respostas da API em cache e não reabre o teste já registrado. As versões estão em `ripe_atlas_fluxos/requirements.txt`.

## Equipe

- Davi Gabriel Borges dos Santos
- Fernanda Akemi Martins Sanpei
- Geziel de Andrade
- Hendrick Ambriola
- Isaac William Braz
