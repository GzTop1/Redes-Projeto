# Memorando de Decisão — Fonte de Dados do Projeto

| Campo | Informação |
| - | - |
| Link do GIT: https://github.com/GzTop1/Redes-Projeto.git |
| Curso / Disciplina | Estrutura de Dados II |
| Projeto integrador | `\[\]` |
| Orientador(a) | `Andrea Ono Sakai` |
| Data de entrega desta etapa | 08/09 |
| Integrantes do grupo | Isaac william, Geziel de Andrade, Fernanda Akemi Martins Sanpei, Hendrick Ambriola, Davi Gabriel Borges dos Santos |



> Preencha cada seção com o que você encontrou na pesquisa. Não deixe nenhum campo com o texto entre colchetes — substitua pelo seu conteúdo. Toda informação levantada nas Opções A e B precisa indicar a fonte de onde veio.

## 1. Situação

A equipe precisa decidir entre utilizar um dataset público pré-existente ou a API do RIPE Atlas para a coleta de dados de medição ICMP, garantindo que o pipeline receba dados válidos para extração de latência, perda e jitter.

## 2. Opção A — Dataset real

- **Origem / link:** CAIDA (Center for Applied Internet Data Analysis) — Archipelago (Ark) Topology Data ([https://www.caida.org/projects/ark/topo_datasets](https://www.caida.org/projects/ark/topo_datasets))

- **Formato:** Archival Format / scamper warts (conversível para JSON, CSV ou plain text).

- **Período coberto:** Coleta contínua desde 2007 até o presente (atualizado diariamente).

- **Campos disponíveis:** Endereço IP de origem, endereço IP de destino, timestamp de envio/resposta, RTT (Round-Trip Time/latência em ms), TTL, e status da resposta (para identificação de perda de pacotes).

- **Licença de uso:** CAIDA Data Acceptable Use Agreement (Gratuita para fins acadêmicos e de pesquisa mediante cadastro).

**Resumo do que foi encontrado:**

Segundo a documentação oficial da CAIDA (2026), o dataset Archipelago realiza prospecções ativas de ICMP traceroute/ping em escala global. Os dados brutos são disponibilizados no formato **warts **(gerados pela ferramenta scamper) e contêm medições precisas de tempo de resposta (RTT) e perda de pacotes para milhares de prefixos IPv4/IPv6, permitindo extrair diretamente a latência, perda e variação de latência (jitter) sem necessidade de infraestrutura própria de medição.

## 3. Opção B — API do RIPE Atlas

- **Documentação consultada (link):** RIPE Atlas REST API Manual — documentação oficial da RIPE NCC ([https://atlas.ripe.net/docs/apis/](https://atlas.ripe.net/docs/apis/)), especificamente as páginas de criação de medições ([https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/creating-measurements/](https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/creating-measurements/)) e de obtenção de resultados ([https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/results-and-latest/](https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/results-and-latest/))

- **Autenticação exigida:** API Key (Chave de API) enviada via cabeçalho HTTP (Authorization: Key \<sua-chave\>) ou parâmetro de URL. Para criar medições ativas, é necessário consumir créditos do RIPE Atlas.

- **Como se cria uma medição:** Envia-se uma requisição HTTP POST para o endpoint /api/v2/measurements/ com um corpo JSON definindo o tipo (type: "ping"), os alvos (target), o número de pacotes, o intervalo e o tipo de sondas a serem utilizadas.

- **Como se consultam os resultados:** Realiza-se uma requisição HTTP GET no endpoint /api/v2/measurements/\{id\}/results/. Os resultados retornam em formato JSON detalhado, contendo arrays com os valores individuais de RTT de cada pacote ICMP enviada por cada sonda.

**Resumo do que foi encontrado:**

Conforme a documentação oficial da RIPE NCC, a API do RIPE Atlas possibilita a execução programática de medições ICMP personalizadas em tempo real a partir de milhares de sondas físicas distribuídas pelo mundo. A API retorna respostas estruturadas em JSON contendo o tempo individual de cada pacote RTT, o que permite calcular facilmente a latência média, a taxa de perda e o jitter. Porém, exige gerenciamento de créditos na plataforma e chave de API para medições ativas.

## 4. Comparação

| Critério | Opção A — Dataset real (CAIDA Ark) | Opção B — API RIPE Atlas |
| - | - | - |
| Controle sobre a coleta | Baixo: a coleta é pré-definida pela infraestrutura da CAIDA. Não é possível escolher alvos pontuais em tempo real, alterar frequências ou customizar pacotes sob demanda. | Alto: controle total sobre os parâmetros. O usuário define o alvo exato (IP ou domínio), o protocolo, a frequência, o número de pacotes e os pontos de origem. |
| Diversidade geográfica | Moderada a alta (foco em infraestrutura): dezenas de monitores dedicados instalados principalmente em backbones, universidades e datacenters parceiros globalmente. | Muito alta (foco na borda da rede): mais de 10.000 sondas ativas distribuídas globalmente, cobrindo milhares de ASNs em conexões residenciais, corporativas, IXPs e datacenters. |
| Custo / complexidade de implementação | Custo financeiro gratuito, porém complexidade alta: exige download de arquivos pesados e descompactação no formato binário .warts para extração em CSV/JSON. | Custo baseado em créditos, complexidade baixa a moderada: comunicação via API REST padrão, com payload e respostas diretamente em JSON, integrável com qualquer linguagem. |
| Tempo até os primeiros dados estarem disponíveis | Lento a moderado: depende da aprovação cadastral do formulário de acesso da CAIDA, somado ao tempo de download e processamento dos dumps brutos. | Imediato a poucos minutos: uma vez criada a medição via requisição POST autenticada, as sondas disparam e os primeiros resultados JSON ficam acessíveis via GET quase em tempo real. |


## 5. Recomendação

| Recomenda-se adotar a *Opção B (API do RIPE Atlas)* como fonte primária de dados para esta etapa, mantendo a *Opção A (CAIDA Ark)* como fonte de contingência e validação cruzada.

A escolha se apoia em três fatores da comparação da Seção 4:

1. *Controle sobre a coleta* — o pipeline precisa extrair latência, perda e jitter de alvos específicos; a RIPE Atlas permite definir exatamente o protocolo (ICMP ping), o alvo, a frequência e o número de pacotes, enquanto o CAIDA Ark oferece apenas medições pré-definidas pela própria infraestrutura, sem possibilidade de customização sob demanda.
2. *Complexidade de implementação* — os resultados da RIPE Atlas já chegam em JSON estruturado via requisições REST padrão, reduzindo o esforço de parsing frente ao formato binário warts da CAIDA, que exige download de arquivos pesados e uma etapa extra de conversão antes de alimentar o pipeline.
3. *Diversidade geográfica na borda da rede* — as mais de 10.000 sondas da RIPE Atlas cobrem conexões residenciais, corporativas e IXPs, o que é mais representativo de cenários reais de uso do que os monitores da CAIDA, concentrados em backbones e datacenters.

*Plano de contingência:* se a API do RIPE Atlas ficar indisponível, esgotar créditos ou sofrer rate limiting durante o desenvolvimento, a equipe usará o dataset CAIDA Ark (já convertido para CSV/JSON) como fonte alternativa. Recomenda-se também salvar localmente os resultados JSON obtidos via RIPE Atlas assim que coletados, evitando depender de novos créditos em caso de reexecução dos testes. |

## 6. Justificativa

| Tanto o CAIDA Ark quanto a RIPE Atlas realizam medição ativa em escala global, mas o que o pipeline precisa não é apenas "ter" latência, perda e jitter — é poder *definir o alvo, o momento e a frequência da medição* para gerar dados controlados e repetíveis durante o desenvolvimento e os testes. Nesse ponto concreto, os dois sistemas divergem:

- *Controle do alvo e do experimento:* o Ark executa apenas as medições já programadas pela própria infraestrutura da CAIDA, entre monitores e prefixos definidos por ela (Seção 2). A equipe não escolhe o IP/domínio de destino nem o momento da coleta. Já na Atlas, a equipe define o alvo via target e dispara a medição sob demanda com POST /api/v2/measurements/ (Seção 3), o que é indispensável para testar o pipeline contra hosts específicos do próprio projeto.
- *Formato e tempo até o dado utilizável:* a Atlas devolve o RTT de cada pacote já em JSON estruturado via GET /.../results/, pronto para alimentar o cálculo de latência média, perda e jitter em minutos. O Ark distribui os dados brutos em .warts, que exige conversão antes de qualquer extração (comparação da Seção 4, linhas "Custo/complexidade" e "Tempo até os primeiros dados").
- *Aderência a cenários reais de borda:* as mais de 10.000 sondas da Atlas estão em conexões residenciais, corporativas e IXPs, enquanto os monitores do Ark ficam concentrados em backbones e datacenters (Seção 4, linha "Diversidade geográfica"). Para um pipeline que quer caracterizar a experiência de rede do usuário final, a borda é o ambiente mais representativo.

Ou seja, o diferencial da Atlas para X = [latência, perda, jitter] não é a existência da métrica — que o Ark também produz — mas o *controle do alvo, a customização da frequência e o formato JSON imediato*, que tornam o ciclo de desenvolvimento e teste do pipeline muito mais rápido e repetível. |

## 7. Riscos e limitações

*RIPE Atlas*

| Risco | Mitigação |
| - | - |
| Esgotamento de créditos para criar novas medições | Monitorar o saldo de créditos pela API (https://atlas.ripe.net/docs/credits/) antes de cada rodada de testes e salvar localmente os resultados JSON já coletados, evitando reconsultas desnecessárias. |
| Limitação de taxa (rate limiting) e dependência de serviço externo | Implementar backoff exponencial nas chamadas à API e, em caso de indisponibilidade prolongada, acionar o plano de contingência com o dataset CAIDA Ark (Seção 5). |
| Volatilidade de sondas residenciais (sonda pode ficar offline durante a medição) | Selecionar mais de uma sonda por região na criação da medição e descartar, na análise, resultados de sondas que não responderam ao ciclo completo. |

*CAIDA Ark*

| Risco | Mitigação |
| - | - |
| Atraso por burocracia de acesso (aprovação cadastral) | Solicitar o cadastro no início do projeto, mesmo usando a Atlas como fonte primária, para já ter a alternativa disponível caso seja necessário acioná-la. |
| Custo computacional de ETL (conversão de .warts para CSV/JSON) | Restringir a conversão aos subconjuntos de dados relevantes ao projeto (prefixos/monitores de interesse) em vez de processar o dump completo. |

### Integrante 1 — `Isaac William Braz`

- **O que fez nesta etapa:** `O que fez nesta etapa: Pesquisa e redação completa dos Tópicos 1 (Situação), 2 (Opção A — Dataset CAIDA) e 3 (Opção B — API RIPE Atlas).`

- **Tempo dedicado (aprox.):** `4h`

- **Evidência da contribuição:** Print do rascunho e das pesquisas dos tópicos 1, 2 e 3 — [prints/evidencia_isaac.png](prints/evidencia_isaac.png)

### Integrante 2 — `Geziel de Andrade`

- **O que fez nesta etapa:** `Pesquisa da comparação`

- **Tempo dedicado (aprox.):** `2h30`

- **Evidência da contribuição:** [prints/evidencia_geziel.png](prints/evidencia_geziel.png)

### Integrante 3 — `Fernanda Akemi Martins Sanpei`

- **O que fez nesta etapa:** `Recomendação`

- **Tempo dedicado (aprox.):** `50min`

- **Evidência da contribuição** *(rascunho):* [prints/evidencia_fernanda.png](prints/evidencia_fernanda.png)

### Integrante 4 — `Hendrick Ambriola`

- **O que fez nesta etapa:** `Justificativa`

- **Tempo dedicado (aprox.):** `40min`

- **Evidência da contribuição** *(rascunho):* [prints/evidencia_hendrick.png](prints/evidencia_hendrick.png)

### Integrante 5 — `Davi Gabriel Borges dos Santos`

- **O que fez nesta etapa:** `Riscos e limitações`

- **Tempo dedicado (aprox.):** `1h10`

- **Evidência da contribuição** *(print de conversa, rascunho):* [prints/evidencia_davi.png](prints/evidencia_davi.png)


## Fontes consultadas

1. [ RIPE Atlas — REST API Manual (visão geral): https://atlas.ripe.net/docs/apis/ ] 
   
2. [ RIPE Atlas — criação de medições (POST /api/v2/measurements/): https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/creating-measurements/ ]

3. [ RIPE Atlas — obtenção de resultados (GET /api/v2/measurements/{id}/results/): https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/results-and-latest/ ]

4. [ RIPE Atlas — créditos: https://atlas.ripe.net/docs/credits/ ]

5. [ RIPE Atlas — mapa e cobertura de sondas: https://atlas.ripe.net/about/probes/ ]

6. [ CAIDA Ark — projeto: https://www.caida.org/projects/ark/ ]
 
7. [ CAIDA Ark — datasets de topologia: https://www.caida.org/projects/ark/topo_datasets ]

8. [ CAIDA — Acceptable Use Agreement: https://www.caida.org/data/acceptable_use_agreement/ ]

9. [ CAIDA — scamper (ferramenta de coleta, formato .warts): https://www.caida.org/catalog/software/scamper/ ]
