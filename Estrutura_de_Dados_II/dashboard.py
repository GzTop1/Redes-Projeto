"""Dashboard do Preditor de Falhas na Rede - Grupo 7.

Rodar localmente:  streamlit run dashboard.py
Precisa, na mesma pasta: modelo.joblib, baseline.csv e preditor.py

Dois modos:
  - Simulado: execuções geradas a partir do baseline do RIPE Atlas (funciona em qualquer lugar).
  - Ping real: ping de verdade em IPs da rede, com baseline PROVISÓRIO calibrado na hora
    (precisa rodar numa máquina com o comando 'ping' e acesso à rede).
"""
import random
import time
from collections import deque
from datetime import datetime

import pandas as pd
import streamlit as st

from preditor import (calcular_baseline, carregar_baseline, carregar_modelo,
                      gerar_execucao, instantaneas, novo_historico, ping_paralelo,
                      prever, rotulo_regra)

ICONE = {"OK": "🟢", "RISCO": "🟡", "FALHA": "🔴"}
MODO_SIM = "Simulado (baseline RIPE Atlas)"
MODO_REAL = "Ping real (baseline provisório)"

st.set_page_config(page_title="Preditor de Falhas", page_icon="📡", layout="wide")


@st.cache_resource
def carregar():
    modelo, feats = carregar_modelo("modelo.joblib")
    return modelo, feats, carregar_baseline("baseline.csv")


modelo, feats, baseline = carregar()
ss = st.session_state
if "rng" not in ss:
    ss.rng = random.Random()
    ss.hist = {}         # fluxo -> fila (máx. 12) das entradas instantâneas (janelas do modelo)
    ss.log = {}          # fluxo -> fila das últimas medições exibidas
    ss.bases_reais = {}  # ip -> baseline provisório calibrado

st.title("📡 Preditor de Falhas na Rede")

# ------------------------------------------------------------------ barra lateral
st.sidebar.header("Modo")
modo = st.sidebar.radio("Fonte das medições", [MODO_SIM, MODO_REAL], label_visibility="collapsed")
real = modo == MODO_REAL

n_hist = st.sidebar.slider("Últimas N medições exibidas", 6, 40, 15)
intervalo = st.sidebar.slider("Intervalo entre execuções (s)", 1, 15, 4)
auto = st.sidebar.checkbox("Execução automática", value=True)
proxima = st.sidebar.button("Gerar próxima execução") if not auto else False

if real:
    st.warning(
        "**Ping real.** Cada execução = 3 pings ICMP aos IPs abaixo. O baseline é **provisório** "
        "(calibrado agora, em minutos), e não os 7 dias que o modelo exige: serve para demonstração.",
        icon="⚠️",
    )
    st.sidebar.header("Dispositivos")
    ips_txt = st.sidebar.text_input("IPs (separados por vírgula)", "8.8.8.8, 192.168.0.1")
    ips = [i.strip() for i in ips_txt.split(",") if i.strip()][:3]
    n_calib = st.sidebar.slider("Execuções de calibração", 30, 120, 40,
                                help="Cada execução leva ~3 s. 40 execuções ≈ 2 min.")
    calibrar = st.sidebar.button("🎯 Calibrar baseline")
    fluxos = [ip for ip in ips if ip in ss.bases_reais]
    opcoes = {"Ping real": "NORMAL", "Evento: RISCO": "RISCO", "Evento: FALHA": "FALHA"}
else:
    st.info(
        "Execuções **geradas a partir do baseline** de cada fluxo (P95/P99 do Período A do RIPE Atlas); "
        "não é ping ao vivo. Normais = **BASE**; injetadas = **EVENTO SIMULADO**.",
        icon="ℹ️",
    )
    st.sidebar.header("Fluxos")
    nao_vistos = list(baseline[baseline["conjunto_no_projeto"].str.startswith("nao_visto")].index)
    fluxos = st.sidebar.multiselect("Fluxos (sonda_âncora)", list(baseline.index),
                                    default=nao_vistos[:3], max_selections=4)
    opcoes = {"Normal": "NORMAL", "Evento: RISCO": "RISCO", "Evento: FALHA": "FALHA"}
    calibrar = False


def base_de(fid):
    return ss.bases_reais[fid] if real else baseline.loc[fid].to_dict()


def registrar(fid, ex, origem):
    b = base_de(fid)
    ss.hist[fid].append(instantaneas(b, ex))
    previsao, probs = prever(modelo, feats, ss.hist[fid])
    ss.log[fid].append({
        "hora": datetime.now().strftime("%H:%M:%S"),
        "rtt_ms": None if ex["avg"] is None else round(ex["avg"], 2),
        "perda_%": round(ex["perda"], 1),
        "jitter_ms": None if ex["jitter"] is None else round(ex["jitter"], 3),
        "classe_atual (regra)": rotulo_regra(b, ex),
        "previsão_próxima (modelo)": previsao,
        "origem": origem,
        "_probs": probs, "_p95": b["p95_rtt_A"], "_p99": b["p99_rtt_A"],
    })


def zerar(fid):
    ss.hist[fid] = novo_historico()
    ss.log[fid] = deque(maxlen=40)


# ------------------------------------------------------------------ calibração (modo real)
pulou_tick = False
if real and calibrar:
    if not ips:
        st.error("Informe ao menos um IP.")
    else:
        coletas = {ip: [] for ip in ips}
        barra = st.progress(0.0, text="Calibrando baseline...")
        try:
            for i in range(n_calib):
                for ip, ex in ping_paralelo(ips).items():
                    coletas[ip].append(ex)
                barra.progress((i + 1) / n_calib, text=f"Calibrando baseline... {i + 1}/{n_calib}")
        except RuntimeError as e:
            barra.empty()
            st.error(str(e))
            st.stop()
        barra.empty()
        for ip in ips:
            try:
                ss.bases_reais[ip] = calcular_baseline(coletas[ip])
            except ValueError as e:
                st.error(f"{ip}: {e}")
                continue
            zerar(ip)
            for ex in coletas[ip][-12:]:  # as últimas 12 execuções reais já viram histórico
                registrar(ip, ex, "REAL (calibração)")
        fluxos = [ip for ip in ips if ip in ss.bases_reais]
        pulou_tick = True

if real and not fluxos:
    st.info("Informe os IPs na barra lateral e clique em **Calibrar baseline** para começar.")
    st.stop()
if not fluxos:
    st.warning("Escolha ao menos um fluxo na barra lateral.")
    st.stop()

# ------------------------------------------------------------------ simulação de eventos
st.sidebar.header("🧪 Simular evento")
cenario = {}
for fid in fluxos:
    cenario[fid] = opcoes[st.sidebar.radio(f"{fid}", list(opcoes), key=f"cen_{real}_{fid}")]

# ------------------------------------------------------------------ estado inicial
for fid in fluxos:
    if fid not in ss.hist:
        zerar(fid)
        for _ in range(12):  # modo simulado: aquecimento para as janelas de 12 execuções
            registrar(fid, gerar_execucao(base_de(fid), "OK", ss.rng), "BASE")
    elif not ss.log[fid]:
        registrar(fid, gerar_execucao(base_de(fid), "OK", ss.rng), "BASE")

# ------------------------------------------------------------------ uma rodada de medições
if (auto or proxima) and not pulou_tick:
    reais = [f for f in fluxos if real and cenario[f] == "NORMAL"]
    try:
        medidas = ping_paralelo(reais)
    except RuntimeError as e:
        st.error(str(e))
        st.stop()
    for fid in fluxos:
        if fid in medidas:
            registrar(fid, medidas[fid], "REAL (ping)")
        elif cenario[fid] == "NORMAL":
            registrar(fid, gerar_execucao(base_de(fid), "OK", ss.rng), "BASE")
        else:
            registrar(fid, gerar_execucao(base_de(fid), cenario[fid], ss.rng), "EVENTO SIMULADO")

# ------------------------------------------------------------------ painel
colunas = st.columns(len(fluxos))
for col, fid in zip(colunas, fluxos):
    with col:
        ult = ss.log[fid][-1]
        b = base_de(fid)
        st.subheader(f"{'Dispositivo' if real else 'Fluxo'} {fid}")
        rotulo_base = "Baseline provisório" if real else "Baseline"
        st.caption(f"{rotulo_base}: RTT mediano {b['mediana_rtt_A']:.1f} ms · "
                   f"P95 {b['p95_rtt_A']:.1f} · P99 {b['p99_rtt_A']:.1f}")

        prev = ult["previsão_próxima (modelo)"]
        st.markdown(f"### {ICONE[prev]} Próxima execução: **{prev}**")
        atual = ult["classe_atual (regra)"]
        selo = "🔵 REAL" if ult["origem"].startswith("REAL") else ("🟣 SIMULADA" if "SIMUL" in ult["origem"] else "⚪ BASE")
        st.caption(f"Execução atual: {ICONE[atual]} {atual} · {selo} ({ult['origem']}) às {ult['hora']}")
        for classe in ("OK", "RISCO", "FALHA"):
            p = ult["_probs"].get(classe, 0.0)
            st.progress(min(max(p, 0.0), 1.0), text=f"{ICONE[classe]} {classe}: {p:.0%}")

        m1, m2, m3 = st.columns(3)
        m1.metric("RTT", "—" if ult["rtt_ms"] is None else f"{ult['rtt_ms']} ms")
        m2.metric("Perda", f"{ult['perda_%']}%")
        m3.metric("Jitter", "—" if ult["jitter_ms"] is None else f"{ult['jitter_ms']} ms")

        df = pd.DataFrame(list(ss.log[fid])[-n_hist:])
        graf = df[["hora", "rtt_ms"]].copy()
        graf["P95 baseline"] = df["_p95"]
        graf["P99 baseline"] = df["_p99"]
        st.line_chart(graf.set_index("hora"))
        st.dataframe(df.drop(columns=["_probs", "_p95", "_p99"]).iloc[::-1], hide_index=True)

if auto:
    time.sleep(intervalo)
    st.rerun()
