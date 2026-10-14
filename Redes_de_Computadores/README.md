# 🌐 Redes de Computadores

**Profª Denise Braito de Souza**

[⬅ Voltar ao README principal](../README.md)

---

Esta pasta reúne as entregas de Redes do projeto: a coleta de métricas de rede (latência, perda de pacotes e jitter) e os cenários de falha usados para validar o preditor.

## 📚 Entregas

| Entrega | Descrição | Situação |
|---|---|:---:|
| `log_rede.csv` | Log consolidado no formato do contrato de dados: `timestamp, ip, latencia_ms, perda_pacotes_pct, jitter_ms, status_real` | 🚧 |
| Cenários provocados | Desligar interface, saturar tráfego e aumentar o RTT, registrando o efeito nas métricas | 🚧 |
| Simulação no Cisco Packet Tracer | Topologia com os cenários de falha reproduzidos | 🚧 |
| Monitoramento local | Ping contínuo para 2 ou mais IPs da rede local | 🚧 |
| Documento de coleta e cenários | Como as métricas foram coletadas e o que cada cenário provoca | 🚧 |

## 🔗 Relação com as outras matérias

- A coleta via RIPE Atlas e o cálculo de latência, perda e jitter estão documentados em [Estrutura de Dados II](../Estrutura_de_Dados_II/) (Tarefa 1 e notebook).
- O `log_rede.csv` alimenta o painel de monitoramento modelado em [Análise de Sistemas](../analise_de_sistemas/).
