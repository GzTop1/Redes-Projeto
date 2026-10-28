# 🌐 Redes de Computadores

**Profª Denise Braito de Souza**

[⬅ Voltar ao README principal](../README.md)

---

Pergunta norteadora do projeto: **como usar medições ICMP para antecipar sinais de falha na rede?**

Em Redes, o projeto é avaliado por um **vídeo de demonstração e explicação do monitoramento e da predição**: primeiro a rede local simulada no Cisco Packet Tracer, depois o aplicativo real monitorando hosts por ICMP.

## 🎬 Entrega

| Item | Regra |
|---|---|
| O quê | Link do vídeo de demonstração e explicação do projeto |
| Valor | Até **3,0 pontos da A2** |
| Duração | **10 a 15 minutos** |
| Formato | YouTube **não listado** |
| Visual | Imagens ao fundo e apresentador num dos cantos da tela, sem atrapalhar a visão |
| Onde entregar | **Somente** pela atividade do Blackboard (não vale e-mail ou mensagem) |
| Tentativas | Até 3; vale a última |
| **Prazo** | **11/11/2026, sem prorrogação** |

> Sem o link, ou com um link que não abre para a professora, a nota do projeto em Redes é zerada. Antes de entregar, abra o link numa janela anônima.

## 📚 O que compõe a entrega

| Parte | Descrição | Arquivo | Situação |
|---|---|---|:---:|
| Rede local no Packet Tracer | Topologia TCP/IP, protocolos por camada, ping entre os hosts e enlace derrubado | [`Plano_Packet_Tracer.md`](Plano_Packet_Tracer.md) e o `.pkt` | ⏳ |
| Aplicativo de monitoramento | Ping (Echo Request/Reply) a hosts da rede local, baseline do host, classificação OK/RISCO/FALHA ao vivo, histórico, alertas e botão de simulação | código do app | ⏳ |
| Testes | Cenários **normal, instável e indisponível**, reais e simulados | histórico do aplicativo + gravações | ⏳ |
| Validação | Comparação da previsão com a ocorrência real e com o resultado do Packet Tracer | tabela no plano | ⏳ |
| Roteiro do vídeo | Introdução, objetivo, desenvolvimento e encerramento | [`Roteiro_Video.md`](Roteiro_Video.md) | ✅ |
| Vídeo | Gravado, no YouTube como não listado, link no Blackboard | link | ⏳ |

## 🧱 Protocolos por camada (arquitetura TCP/IP)

| Camada | Protocolos pedidos | Onde aparecem no projeto |
|---|---|---|
| Aplicação | HTTP/HTTPS, DNS, FTP/SFTP | Servidor web e DNS no Packet Tracer; o app consulta a API do RIPE Atlas por HTTPS e o painel abre no navegador por HTTP |
| Transporte | TCP, UDP | TCP no HTTP/HTTPS e no FTP; UDP no DNS |
| Rede | IPv4, IPv6, **ICMP**, roteamento | Endereçamento IPv4 (e IPv6 opcional) da rede local; **ping ICMP Echo Request/Echo Reply**, base de todo o monitoramento; rota entre as duas redes no roteador |
| Enlace | ARP, Ethernet | ARP descobrindo o MAC antes do primeiro ping; quadros Ethernet entre PC, switch e roteador |

## 🔗 Relação com as outras matérias

- **Estrutura de Dados II:** o modelo (Random Forest, com a árvore de decisão como versão legível) foi treinado com medições reais de ping do RIPE Atlas. Como as 21 variáveis são relativas ao baseline de cada caminho, o mesmo modelo serve para um host da rede local depois que o app monta o baseline dele. Ver [Estrutura de Dados II](../Estrutura_de_Dados_II/).
- **Análise e Projeto de Sistemas:** requisitos, casos de uso e diagramas do aplicativo. Ver [Análise de Sistemas](../analise_de_sistemas/).
