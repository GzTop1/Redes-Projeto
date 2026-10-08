# Diário da Tarefa 1 — Problema e coleta bruta (sem rótulo)

**Período:** 17/08/2026 a 17/09/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)  
**Modelo desta disciplina:** árvore de decisão. Nesta tarefa não se treina árvore.

**Equipe:** Grupo 7  
**Integrantes:** Isaac William Braz, Fernanda Akemi Martins Sanpei, Geziel de Andrade, Hendrick Ambriola, Davi Gabriel Borges dos Santos, Victor Gabriel Alves  
**Scrum Master da tarefa:** Isaac William Braz  
**Repositório GitHub:** https://github.com/GzTop1/Redes-Projeto

> Esta tarefa entrega o problema e o **dado cru**. Não há classe OK, RISCO ou FALHA. Não há baseline, não há mediana e não há árvore. Quem rotular aqui mistura a coleta com a decisão da Tarefa 2.
>
> A rota entra na coleta só para haver caminhos curtos e longos no mesmo arquivo. RTT alto **não** é falha. País, IP e nome da rota **não** serão coluna da árvore.

### Contrato desta tarefa

| | Artefato | Quem usa depois |
|---|---|---|
| **Entra** | RFC do projeto | — |
| **Sai** | RFC preenchido pelo grupo (problema, horizonte, custo de errar FALHA, fora de escopo) | Tarefas 2 e 5 |
| **Sai** | Dicionário v0.1 só com colunas **brutas** da medição | Tarefa 2 |
| **Sai** | `data/raw/` + `config/` + `requirements.txt` | Tarefa 2 **é obrigada a usar este bruto** |
| **Sai** | Este diário | Tarefas seguintes |

**Não sai daqui:** baseline, rótulo, `z_robusto`, split, árvore, métrica de modelo.

---

## 1. Definição do problema

Responder no diário. A resposta tem de bater com o RFC.

| Pergunta | Resposta do grupo |
|---|---|
| Qual evento a árvore vai classificar? | Degradação do fluxo em relação ao **próprio** normal: OK, RISCO ou FALHA. Não é “rota longa” nem “RTT acima de 100 ms”. |
| O que é um fluxo? | `fluxo_id = probe_id \| dst_addr`. Cada destino tem um `msm_id` do Anchoring Mesh (16 medições usadas na coleta, 14 na tabela final). |
| O que é cada linha do bruto? | Uma medição ICMP desse fluxo (rajada de 3 pacotes a cada 240 s), com timestamp. Ainda **sem** classe. |
| Qual horizonte fica para depois? | Detector: estado da medição atual. Preditor: estado 12 minutos à frente (3 intervalos de 240 s). A árvore só entra na Tarefa 3. |
| Quem usa o alerta? | Quem opera o enlace: investigar (FALHA), observar (RISCO) ou não agir (OK). |
| O que está proibido como definição de falha? | Limiar global de RTT, país, continente ou nome da rota. |

- [x] RFC do grupo preenchido a partir desta tabela (`RFC_Preditor_Degradacao_Rede_Grupo7.md`)
- [x] Dicionário v0.1 só com variáveis brutas (notebook, seção 1.7)

## 2. O que coletar (e o que não criar)

Fonte: medições públicas já existentes de ping IPv4 (mesh de Anchors do RIPE Atlas, somente `GET`). Não criar medição própria e não gastar crédito.

| Campo | Unidade | Papel agora | No notebook |
|---|---|---|---|
| `timestamp` | UTC | Ordenar o fluxo | `timestamp` e `timestamp_utc` |
| `measurement_id` | — | Identidade da medição | `msm_id` |
| `probe_id` | — | Origem | `prb_id` |
| `dst_addr` | — | Destino | `dst_addr` |
| `fluxo_id` | texto estável | `probe_id\|dst_addr` | `fluxo_id` |
| RTT da rajada (médio; mín/máx) | ms | Vazio se não houver resposta. **Nunca 0** | `avg`, `min`, `max` (o `-1` do RIPE vira vazio) |
| enviados, recebidos | contagem | | `sent`, `rcvd` |
| `perda_pct` | % | `(enviados − recebidos) / enviados × 100` | `perda_pct` |
| `jitter_ms` | ms | Desvio-padrão dos RTT da rajada só com 2 ou mais respostas; senão, vazio | `jitter_ms` |
| `timeout_atual` | 0 ou 1 | 1 se não há RTT ou perda = 100% | `timeout_atual` |
| país ou rota | texto | Só auditoria. **Fora da futura árvore** | `config/tabela_desenho.csv` (`rota`, `escopo`) |

Regras da coleta:

- [x] Vários fluxos, com pelo menos um caminho curto e um caminho longo no mesmo período: **64 fluxos em 8 rotas** (curto, regional e longo)
- [x] A diversidade geográfica está documentada e **não** virou classe (`escopo` só em `config/`)
- [x] Dois blocos de tempo contíguos, sem amostra nos dois: Período A de 06/09/2026 04:32 a 13/09/2026 04:32 UTC; Período B de 13/09/2026 04:32 a 20/09/2026 04:32 UTC
- [x] Timeout permanece no arquivo (227 timeouts na tabela final)
- [x] JSON bruto preservado; a tabela tratada vai para `data/interim/` e não apaga o bruto
- [x] Parâmetros (período, probes, destinos) em `config/` (`parametros.json`, `destinos_com_msm_v2.csv`, `tabela_desenho.csv`)
- [x] HTTP com timeout de 120 s, 3 tentativas em erro 429/5xx e coleta idempotente (arquivo do dia que já existe é pulado; gravação atômica)
- [x] `requirements.txt` da coleta (pandas 2.2.3, numpy 2.1.3, requests 2.32.4)

**Desenho da coleta:**

| Rota | Escopo (só auditoria) | Destinos | Fluxos |
|---|---|---|---|
| BR→BR | curto | Porto Alegre, São Paulo | 8 |
| DE→DE | curto | Frankfurt, Mainz | 8 |
| BR→AR | regional | Bahía Blanca, Buenos Aires | 8 |
| BR→CL | regional | Santiago de Chile, Santiago | 8 |
| DE→NL | regional | Amsterdam, Apeldoorn | 8 |
| BR→DE | longo | Frankfurt, Mainz | 8 |
| BR→JP | longo | Tokyo, Tsuchiura | 8 |
| BR→US | longo | Durham, Detroit | 8 |

**Decisão documentada:** na primeira passagem, 12 dos 64 fluxos (destinos Tostado/AR e Nuremberg/DE) ficaram com 100% de timeout nos 14 dias e continuavam sem resposta nas últimas 6 horas. Os dois destinos foram trocados por Buenos Aires e Mainz, escolhidos pela mesma regra e conferidos no início do Período A e no fim do Período B. Os arquivos antigos continuam em `data/raw/` e a tabela anterior está em `config/tabela_desenho_v1_descartada.csv`.

**Evidências (notebook, commit, trecho do config):** notebook `Projeto_Preditor_Falhas_PPF_.ipynb`, seções 1.2 a 1.7; `config/parametros.json`; `config/tabela_desenho.csv`; `config/evidencias.jsonl`; prints em https://github.com/GzTop1/Redes-Projeto/tree/main/prints/Isaac/Tarefa_1

## 3. Relatório de qualidade — ainda sem classe

- [x] Registros por `fluxo_id`: de 5.011 a 5.039 por fluxo (mediana 5.034), de 5.040 esperados
- [x] Início e fim de cada fluxo: todos de 06/09/2026 04:32 a 20/09/2026 04:31 UTC (detalhe por fluxo em `data/interim/relatorio_qualidade_por_fluxo.csv`)
- [x] Campos ausentes: `min`, `avg` e `max` vazios em 227 medições; `jitter_ms` vazio em 436 (rajadas com 0 ou 1 resposta). RTT vazio é ausência, não zero.
- [x] Duplicatas: 0
- [x] Quantidade de timeouts: 227 (curto 34, regional 49, longo 144)
- [x] RTT e perda descritos **sem** dizer OK, RISCO ou FALHA:

| Escopo | Fluxos | Registros | RTT mín. (ms) | RTT mediana (ms) | RTT máx. (ms) | Perda mediana | Perda máx. |
|---|---|---|---|---|---|---|---|
| curto | 16 | 80.540 | 1,1 | 9,8 | 79,5 | 0% | 100% |
| regional | 24 | 120.772 | 6,3 | 36,5 | 915,3 | 0% | 100% |
| longo | 24 | 120.704 | 120,9 | 206,1 | 1.591,9 | 0% | 100% |

**N de registros brutos:** 322.016 na tabela de trabalho final (161.135 no Período A e 160.881 no B), lidos de 224 arquivos JSON. Na primeira passagem, antes da troca de destinos, eram 322.039. `data/raw/` tem 266 arquivos (178 MB).  
**N de fluxos:** 64 (14 destinos, cada um medido por 4 probes de origem; 11 probes distintos ao todo), nenhum abaixo de 1.500 RTT válidos no Período A.  
**Caminho curto e caminho longo presentes (quais):** curtos BR→BR e DE→DE; regionais BR→AR, BR→CL e DE→NL; longos BR→DE, BR→JP e BR→US.

## 4. Scrum

- [x] Product Owner = docente; Scrum Master da tarefa = Isaac William Braz; time de desenvolvimento = os seis integrantes do Grupo 7
- [ ] Board com To do / Doing / Done
- [x] Pelo menos 3 histórias: coletar fluxos diversos; preservar o bruto com timeout; separar Período A e Período B sem rotular

**Histórias:**  
1. Como grupo, quero coletar fluxos curtos, regionais e longos no mesmo período, para que o baseline de cada fluxo represente o próprio normal e a distância não vire classe. *Critério de aceite:* 64 fluxos em 8 rotas, todos com dados nos 14 dias.  
2. Como grupo, quero preservar o JSON bruto com os timeouts, para que nenhuma ausência de resposta vire RTT 0 e a Tarefa 2 possa refazer tudo a partir do bruto. *Critério de aceite:* 266 arquivos intactos em `data/raw/`; 227 RTT vazios e nenhum RTT 0 na tabela de trabalho.  
3. Como grupo, quero separar o Período A e o Período B sem rotular, para que o baseline seja calculado só com o passado. *Critério de aceite:* A de 06/09 a 13/09 e B de 13/09 a 20/09, sem timestamp em comum; nenhuma coluna de classe nesta tarefa.

**Link do board:** _https://github.com/users/GzTop1/projects/1_

## 5. Diário de bordo

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Isaac William Braz | Configuração do projeto no Google Drive; descoberta das Anchors e dos `msm_id` do mesh; tabela de desenho com 64 fluxos; coleta dia a dia dos Períodos A e B; diagnóstico e troca dos destinos sem resposta (Tostado e Nuremberg por Buenos Aires e Mainz); tabela de trabalho e relatório de qualidade; dicionário v0.1. | 12 fluxos com 100% de timeout na primeira passagem, que exigiram diagnóstico e troca de destinos sem apagar o bruto; volume da coleta (266 arquivos, 178 MB) e tempo de download. | Manter a coleta idempotente, os parâmetros em `config/` e o registro de cada decisão no `evidencias.jsonl`. |
| Fernanda Akemi Martins Sanpei | Não atuei diretamente nesta tarefa (responsável: Isaac). | — | — |
| Geziel de Andrade | Não atuei diretamente nesta tarefa (responsável: Isaac). | — | — |
| Hendrick Ambriola | Não atuei diretamente nesta tarefa (responsável: Isaac). | — | — |
| Davi Gabriel Borges dos Santos | Não atuei diretamente nesta tarefa (responsável: Isaac). | — | — |
| Victor Gabriel Alves | Não atuei diretamente nesta tarefa (responsável: Isaac). | — | — |

## 6. Evidências gerais

- Link do RFC: _https://github.com/GzTop1/Redes-Projeto/blob/main/Projeto_Preditor_Redes_Grupo7/RFC_Preditor_Degradacao_Rede_Grupo7.md_
- Link do dicionário v0.1: notebook `Projeto_Preditor_Falhas_PPF_.ipynb`, seção 1.7
- Link dos commits: https://github.com/GzTop1/Redes-Projeto/commits/main
- Link de `data/raw/` e do `config/`: _https://drive.google.com/drive/folders/1OrkS3nEqfN4gc53uTRT9WUrMwwWddhYc?usp=sharing_

---

## Rubrica — Tarefa 1 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Problema | 0,5 | Fluxo, unidade de análise e proibição de RTT absoluto como falha estão explícitos | | |
| Coleta bruta | 1,5 | Vários fluxos (curto e longo), timeout preservado, RTT vazio ≠ 0, config externa, bruto intocável | | |
| Período A e Período B sem rótulo | 1,0 | Dois blocos sem sobreposição; relatório de qualidade **sem** classe | | |
| Scrum + diário | 1,0 | Papéis, board, histórias e diário de todos | | |
| **Total** | **4,0** | | **___ / 4,0** | |
