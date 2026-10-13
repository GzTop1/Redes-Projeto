# Diário da Tarefa 5 — Modelo final e teste único

**Período:** 12/10/2026 a 25/10/2026  
**Projeto:** Preditor de degradação de rede relativo ao baseline do fluxo (independente da rota)

**Equipe:** Grupo 7  
**Scrum Master da tarefa:** Geziel de Andrade  
**Repositório GitHub:** https://github.com/GzTop1/Redes-Projeto

> A árvore que entra aqui é a da Tarefa 4. O baseline e o rótulo são os da Tarefa 2. O teste, guardado desde a Tarefa 2, é medido **uma vez**.
>
> Continua sendo uma árvore de decisão. O grupo entrega as regras, a matriz e o que a árvore faz num fluxo que ela não viu — desde que esse fluxo tenha a própria ficha de baseline, calculada só no período inicial dele.


### Contrato desta tarefa

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Corte da Tarefa 2 e ficha de baseline | Tarefa 2 |
| **Entra** | Modelo ajustado | Tarefa 4 |
| **Sai** | Teste único: matriz 3×3, F1 por classe, F1 macro | Entrega |
| **Sai** | Checagem de fluxos não vistos, com baseline próprio | Entrega |
| **Sai** | Ficha do modelo (`ficha_do_modelo.json`) e dicionário v0.4 | Entrega |

Não há tarefa seguinte.

- [x] Os hiperparâmetros não foram escolhidos olhando o teste (modelo congelado em `data/processed/modelo_final_congelado.json` antes da abertura)
- [x] O baseline não usou medição do teste (ficha só do Período A)

---

## 1. Modelo que será medido

- [x] Família, parâmetros e colunas
- [x] Confirmação por código de que país, IP, rota e RTT absoluto não estão no modelo
- [ ] Três regras em português: não se aplica ao Random Forest. Como referência legível, ficam as regras da árvore da Tarefa 3 (diário da Tarefa 3, seção 2).

**Parâmetros:** Random Forest, 200 árvores, `max_depth` None, `min_samples_leaf` 5, `max_features` sqrt, `class_weight` None, semente 42. F1 macro na validação: 0,7702.  
**Colunas (21):** `perda_pct`, `rtt_ausente`, `razao_rtt_p95`, `razao_rtt_p99`, `razao_jitter_p95`, `amplitude_rtt_rel`, `delta_ttl_clip`, `ttl_reset`, `perda_media_wN`, `rtt_p95_max_wN`, `jitter_p95_max_wN`, `n_rtt_acima_p95_wN` (N = 3, 6, 12) e `perdas_consecutivas`.  
**País, IP, rota e RTT absoluto no modelo:** não (o notebook faz `assert` para `anchor_pais`, `probe_pais`, `anchor_ip`, `rtt_ms`, `rota`, `probe_asn` e `faixa_distancia`).

## 2. Teste temporal

Fluxos conhecidos, último dia do Período B (de t0 + 6 dias + 60 min até 05/10/2026 18:00 UTC), **40.453 medições** de 118 fluxos. Teste aberto em **11/10/2026 14:35:52 UTC** (`teste_unico.json`).

- [x] Matriz 3×3 com contagem
- [x] Precisão, recall e F1 de OK, RISCO e FALHA
- [x] F1 macro
- [x] Recall de FALHA e troca RISCO ↔ FALHA comentados
- [x] Dois casos: um acerto em caminho longo (OK) e um erro relevante

**Matriz (linha = classe real da próxima medição):**

| | prev. OK | prev. RISCO | prev. FALHA |
|---|---|---|---|
| **real OK** | 34.632 | 105 | 46 |
| **real RISCO** | 2.097 | 1.983 | 156 |
| **real FALHA** | 253 | 235 | 946 |

| Classe | Precisão | Recall | F1 | Suporte |
|---|---|---|---|---|
| OK | 0,9365 | 0,9957 | 0,9652 | 34.783 |
| RISCO | 0,8536 | 0,4681 | 0,6047 | 4.236 |
| FALHA | 0,8240 | 0,6597 | 0,7328 | 1.434 |

**F1 macro no teste: 0,7675** (balanced accuracy 0,7078; acurácia 0,9285).

| Referência no mesmo teste | F1 macro |
|---|---|
| Modelo final | **0,7675** |
| Persistência (repetir a classe atual) | 0,7302 |
| Classe majoritária ("sempre OK") | 0,3082 |

**Recall de FALHA e troca RISCO ↔ FALHA:** recall de FALHA de 0,6597. Das 1.434 FALHAs reais, 235 foram previstas como RISCO e 253 como OK. No sentido inverso, 156 RISCOs viraram FALHA. O erro dominante continua sendo RISCO previsto como OK (2.097).

**Casos:**
- **Acerto em caminho longo (OK):** fluxo `6380_1880` (destino Dallas/US, faixa longa), 04/10/2026 19:03:17 UTC. Classe atual OK, próxima OK, prevista OK. A distância não virou alerta.
- **Erro relevante (FALHA prevista como OK):** fluxo `6407_1360` (destino Mutterstadt/DE, faixa média), 05/10/2026 08:45:44 UTC. Classe atual OK, próxima FALHA, prevista OK. É um início de falha sem sinal na medição atual, o tipo de erro que o modelo quase nunca acerta.

## 3. Fluxos que o modelo não viu

13 fluxos (10% dos 131) sorteados com a SEED 42 na Tarefa 2, **antes** de qualquer treino. Cada um tem ficha própria do Período A (21/09 a 28/09/2026); a avaliação usa o Período B inteiro deles. Lista em `corte_temporal.json`.

- [x] O fluxo novo não aparece no treino
- [x] Os percentis do baseline não usam o trecho avaliado
- [x] Dizer se um caminho longo estável permaneceu OK e se uma degradação foi marcada RISCO ou FALHA
- [x] Todos com baseline VÁLIDO

**Resultado:** 32.624 medições; **F1 macro 0,6275** contra 0,6207 da persistência; recall de FALHA 0,2659.

| Faixa | Linhas | Degradações reais | Detectadas (previsão ≠ OK) | OK mantidos como OK |
|---|---|---|---|---|
| curta | 4.985 | 270 | **0** | 4.713 |
| média | 12.573 | 914 | 108 | 11.640 |
| longa | 15.066 | 2.240 | 1.347 | 12.762 |

- **Caminho longo:** 12.762 OK mantidos como OK, e 60% das degradações detectadas. A distância não gerou falso alarme em massa.
- **Caminho curto:** **nenhuma** das 270 degradações foi detectada. Em fluxo curto e desconhecido, o modelo não serve como alerta.

## 4. O que declarar

- [x] **O modelo prevê a classe da próxima medição (cerca de 4 min).** A classe atual não é variável; as 21 variáveis usam só o presente e o passado do fluxo.
- [x] **Contra a persistência:** no teste, F1 macro de 0,7675 contra 0,7302 (+0,0373).
- [x] **Detector ou preditor:**

  | Fatia do teste | Resultado |
  |---|---|
  | Transições (a classe muda de t para t+1) | F1 macro 0,2344 |
  | Inícios de FALHA (estava OK/RISCO, a próxima é FALHA; 411 casos) | recall de FALHA 0,0195 |

  **Conclusão:** há ganho geral sobre a persistência, mas o modelo **antecipa pouco os inícios de FALHA**. O ganho vem de manter a classe quando ela não muda. Ele funciona como um **detector suavizado**, não como um alerta antecipado.
- [x] **Limitações:**
  - A classe é uma política de rótulo relativa ao P95/P99 do próprio fluxo, não uma falha confirmada na rede. Em fluxo estável, cerca de 5% das linhas passam do P95 por definição.
  - 14 dias de dados (7 de baseline e 7 de dataset); o teste é um único bloco de cerca de 1 dia.
  - Só ICMP/IPv4; 3 pacotes por execução (perda só 0, 33, 67 ou 100%).
  - Todas as sondas de origem são âncoras de data center; não representam a rede de acesso.
  - Fluxos com cobertura baixa ficam de fora; destinos sem fluxo utilizável: 4227 (Changhua/TW) e 4862 (Antananarivo/MG).
  - Baseline fixo; não acompanha deriva lenta.
  - Generalização fraca em caminhos curtos não vistos.

## 5. Ficha do modelo

| Campo | Conteúdo |
|---|---|
| Problema | Classe OK, RISCO ou FALHA da **próxima** medição de um fluxo, relativa ao baseline do fluxo |
| Unidade | Uma execução de ping de um `id_fluxo` (`probe_id_anchor_id`) no Período B |
| Baseline | Período A (21/09 a 28/09/2026): P95/P99 de RTT e jitter e mediana do TTL; mínimo de 30 RTT válidos; cobertura ≥ 80% |
| Colunas | As 21 variáveis da seção 1 |
| Modelo | Random Forest, 200 árvores, `max_depth` None, `min_samples_leaf` 5, `max_features` sqrt, semente 42 |
| Validação | F1 macro 0,7702 (árvore T3: 0,7691; persistência: 0,7261) |
| Teste (uma vez) | F1 macro 0,7675 (persistência 0,7302; classe majoritária 0,3082); balanced accuracy 0,7078; recall de FALHA 0,6597 |
| Fluxos não vistos | 13 fluxos: F1 macro 0,6275 (persistência 0,6207); faixa curta sem detecção |
| Detector ou preditor | Detector suavizado: recall de 0,0195 nos inícios de FALHA |
| O que ele não faz | Não classifica distância. Não opera em fluxo sem baseline próprio. Não antecipa falhas de forma confiável. |
| Como reproduzir | `requirements.txt` (pandas 2.2.3, numpy 2.1.3, requests 2.32.4, scikit-learn 1.6.1, joblib 1.6.0); notebook `Projeto_Preditor_Falhas_PPF_corrigido_v3.ipynb` executado de cima para baixo; `config/` (`parametros.json`, `tabela_desenho.csv`, `fluxos_modelagem.csv`) e `data/processed/` (`corte_temporal.json`, `modelo_final_congelado.json`, `ficha_do_modelo.json`) |

**Dicionário v0.4:** as 21 colunas acima, mais `alvo` (classe da próxima medição). Só auditoria: `classe_atual`, `rtt_ms`, `id_fluxo`, `anchor_id`, `probe_id`, `timestamp`, `split`. Fora do modelo: país, IP, rota, faixa de distância, ASN e RTT absoluto.

## 6. Scrum e diário

- [X] Board atualizado

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Isaac William Braz | Não atuei diretamente nesta tarefa (responsável: Geziel). | — | — |
| Fernanda Akemi Martins Sanpei | Não atuei diretamente nesta tarefa (responsável: Geziel). | — | — |
| Geziel de Andrade | Modelo congelado antes do teste; teste único (matriz, F1, balanced accuracy, comparação com persistência e classe majoritária); fatias de transição e início de falha; fluxos não vistos; limitações; ficha do modelo e dicionário v0.4. | Abrir o teste uma única vez e interpretar o resultado contra a persistência. | Declarar as limitações com clareza e manter a ficha alinhada às colunas usadas. |
| Hendrick Ambriola | Não atuei diretamente nesta tarefa (responsável: Geziel). | — | — |
| Davi Gabriel Borges dos Santos | Não atuei diretamente nesta tarefa (responsável: Geziel). | — | — |
| Victor Gabriel Alves | Não atuei diretamente nesta tarefa (responsável: Geziel). | — | — |

**Link do board:** _https://github.com/users/GzTop1/projects/1_

---

## Rubrica — Tarefa 5 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Árvore final legível | 1,0 | Regras em português, colunas relativas, parâmetros da Tarefa 4 | | |
| Teste único | 1,5 | Matriz 3×3 em contagem, F1 por classe, F1 macro, casos curto/longo; teste não escolheu a árvore | | |
| Fluxo novo com baseline próprio | 1,0 | Ficha só no período inicial; ou limitação declarada se faltou fluxo | | |
| Ficha + diário | 0,5 | Ficha preenchida e diário de todos | | |
| **Total** | **4,0** | | **___ / 4,0** | |
