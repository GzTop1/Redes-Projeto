"""Lógica do preditor de falhas (Grupo 7) - sem interface.

Reproduz o cálculo das 21 entradas descrito em metadados.json e gera execuções
simuladas a partir do baseline de cada fluxo (P95/P99 de RTT e jitter do Período A).
"""
import glob
import io
import math
import os
import platform
import random
import re
import statistics
import subprocess
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor

import joblib
import numpy as np
import pandas as pd

JANELAS = (3, 6, 12)
N_PACOTES = 3
CLASSES_ROTULO = ("OK", "RISCO", "FALHA")


# ---------------------------------------------------------------- carga de arquivos
def carregar_modelo(caminho="modelo.joblib"):
    """Carrega o modelo inteiro (modelo.joblib) ou, se ele não existir, junta
    modelo.joblib.parte1, .parte2... (o GitHub pelo navegador só aceita arquivos de até 25 MB)."""
    if os.path.exists(caminho):
        d = joblib.load(caminho)
    else:
        partes = sorted(glob.glob(caminho + ".parte*"))
        if not partes:
            raise FileNotFoundError(f"Não achei {caminho} nem {caminho}.parte1/.parte2")
        dados = b"".join(open(p, "rb").read() for p in partes)
        d = joblib.load(io.BytesIO(dados))
    return d["modelo"], d["features"]


def carregar_baseline(caminho="baseline.csv"):
    df = pd.read_csv(caminho)
    df = df[df["baseline_valido"]]
    return df.set_index("id_fluxo")


# ---------------------------------------------------------------- uma execução de ping
def resumir_execucao(rtts, ttl):
    """rtts: lista de N_PACOTES valores (float em ms, ou None para pacote perdido)."""
    validos = [r for r in rtts if r is not None]
    perda = (len(rtts) - len(validos)) / len(rtts) * 100
    if not validos:
        return {"perda": perda, "avg": None, "mn": None, "mx": None, "jitter": None, "ttl": None}
    return {
        "perda": perda,
        "avg": sum(validos) / len(validos),
        "mn": min(validos),
        "mx": max(validos),
        "jitter": statistics.pstdev(validos) if len(validos) > 1 else 0.0,  # ddof=0
        "ttl": ttl,
    }


def _razao(num, den):
    if num is None or den is None or den == 0:
        return None
    r = num / den
    return r if math.isfinite(r) else None


def rotulo_regra(base, ex):
    """Classe da execução ATUAL, pela regra usada no treino (para na primeira verdadeira)."""
    if ex["perda"] >= 66.0:
        return "FALHA"
    if ex["avg"] is not None and ex["avg"] > base["p99_rtt_A"]:
        return "FALHA"
    if ex["perda"] >= 33.0:
        return "RISCO"
    if ex["avg"] is not None and ex["avg"] > base["p95_rtt_A"]:
        return "RISCO"
    if ex["jitter"] is not None and ex["jitter"] > base["p95_jitter_A"]:
        return "RISCO"
    return "OK"


# ---------------------------------------------------------------- as 21 entradas do modelo
def instantaneas(base, ex):
    """Valores da execução atual; None = ausente (vira -1 na hora de montar o vetor)."""
    amp = None
    if ex["avg"] is not None:
        amp = _razao(ex["mx"] - ex["mn"], ex["avg"])
    if ex["ttl"] is None:
        delta, reset = None, 0.0
    else:
        d = ex["ttl"] - base["ttl_baseline"]
        delta = float(max(-16, min(16, d)))
        reset = 1.0 if abs(d) >= 64 else 0.0
    return {
        "perda_pct": ex["perda"],
        "rtt_ausente": 1.0 if ex["avg"] is None else 0.0,
        "razao_rtt_p95": _razao(ex["avg"], base["p95_rtt_A"]),
        "razao_rtt_p99": _razao(ex["avg"], base["p99_rtt_A"]),
        "razao_jitter_p95": _razao(ex["jitter"], base["p95_jitter_A"]),
        "amplitude_rtt_rel": amp,
        "delta_ttl_clip": delta,
        "ttl_reset": reset,
    }


def montar_features(historico):
    """historico: deque de dicts de instantaneas(), o último é a execução atual."""
    atual = historico[-1]
    f = {k: (-1.0 if v is None else float(v)) for k, v in atual.items()}
    lista = list(historico)
    for w in JANELAS:
        jan = lista[-w:]
        r95 = [x["razao_rtt_p95"] for x in jan if x["razao_rtt_p95"] is not None]
        rj = [x["razao_jitter_p95"] for x in jan if x["razao_jitter_p95"] is not None]
        f[f"perda_media_w{w}"] = sum(x["perda_pct"] for x in jan) / len(jan)
        f[f"rtt_p95_max_w{w}"] = max(r95) if r95 else -1.0
        f[f"jitter_p95_max_w{w}"] = max(rj) if rj else -1.0
        f[f"n_rtt_acima_p95_w{w}"] = float(sum(r > 1 for r in r95)) if r95 else -1.0
    consec = 0
    for x in reversed(lista):
        if x["perda_pct"] > 0:
            consec += 1
        else:
            break
    f["perdas_consecutivas"] = float(consec)
    return f


def prever(modelo, nomes_features, historico):
    """Devolve (classe prevista para a PRÓXIMA execução, {classe: probabilidade})."""
    f = montar_features(historico)
    X = pd.DataFrame([[f[n] for n in nomes_features]], columns=nomes_features)
    proba = modelo.predict_proba(X)[0]
    probs = {c: float(p) for c, p in zip(modelo.classes_, proba)}
    return max(probs, key=probs.get), probs


def novo_historico():
    return deque(maxlen=max(JANELAS))


# ---------------------------------------------------------------- simulação a partir do baseline
def _candidata(base, cenario, rng):
    med, p95, p99 = base["mediana_rtt_A"], base["p95_rtt_A"], base["p99_rtt_A"]
    disp = max(base["mediana_jitter_A"], 1e-3)
    ttl = int(base["ttl_baseline"])

    def rtts(alvo, d):
        return [max(0.01, rng.gauss(alvo, d)) for _ in range(N_PACOTES)]

    if cenario == "OK":
        return rtts(med + (p95 - med) * rng.uniform(-0.2, 0.5), disp)
    if cenario == "RISCO":
        # RTT entre P95 e P99 mantido por várias execuções (é o que o modelo reconhece melhor;
        # perda isolada de 1 pacote ele trata como ruído e prevê OK)
        d = min(disp, (p99 - p95) / 6) if p99 > p95 else disp / 4
        return rtts(p95 + (p99 - p95) * rng.uniform(0.3, 0.8), max(d, 1e-4))
    # FALHA: RTT bem acima do P99 ou perda total dos 3 pacotes
    if rng.random() < 0.6:
        return rtts(p99 * rng.uniform(1.3, 1.8), disp)
    return [None] * N_PACOTES


def gerar_execucao(base, cenario, rng=random):
    """Gera uma execução de 3 pings coerente com o baseline e com a classe pedida."""
    ttl = int(base["ttl_baseline"])
    for _ in range(60):
        ex = resumir_execucao(_candidata(base, cenario, rng), ttl)
        if rotulo_regra(base, ex) == cenario:
            return ex
    fallback = {
        "OK": [base["mediana_rtt_A"]] * 3,
        "RISCO": [(base["p95_rtt_A"] + base["p99_rtt_A"]) / 2] * 3,
        "FALHA": [None, None, None],
    }[cenario]
    return resumir_execucao(fallback, ttl)


# ---------------------------------------------------------------- ping real
_RE_TEMPO = re.compile(r"(?:time|tempo)\s*([=<])\s*([\d.,]+)\s*ms", re.IGNORECASE)
_RE_TTL = re.compile(r"ttl\s*=\s*(\d+)", re.IGNORECASE)


def interpretar_ping(saida, n=N_PACOTES):
    """Extrai (lista de n RTTs com None nos perdidos, ttl) da saída do comando ping."""
    rtts = [float(v.replace(",", ".")) for _, v in _RE_TEMPO.findall(saida)][:n]
    ttls = [int(t) for t in _RE_TTL.findall(saida)]
    rtts = rtts + [None] * (n - len(rtts))
    return rtts, (ttls[-1] if ttls else None)


def ping_execucao(ip, n=N_PACOTES):
    """Uma execução real: n pacotes ICMP ao ip -> dict no formato de resumir_execucao()."""
    so = platform.system().lower()
    if so == "windows":
        cmd = ["ping", "-n", str(n), "-w", "1000", ip]
    elif so == "darwin":
        cmd = ["ping", "-c", str(n), "-W", "1000", ip]
    else:
        cmd = ["ping", "-c", str(n), "-W", "1", ip]
    try:
        saida = subprocess.run(cmd, capture_output=True, text=True, timeout=n * 2 + 5).stdout
    except FileNotFoundError:
        raise RuntimeError("O comando 'ping' não existe nesta máquina (no Streamlit Cloud, por exemplo).")
    except subprocess.TimeoutExpired:
        saida = ""
    rtts, ttl = interpretar_ping(saida, n)
    return resumir_execucao(rtts, ttl)


def ping_paralelo(ips):
    """Pinga vários IPs ao mesmo tempo. Devolve {ip: execução}."""
    if not ips:
        return {}
    with ThreadPoolExecutor(max_workers=len(ips)) as ex:
        return dict(zip(ips, ex.map(ping_execucao, ips)))


MIN_RTT_VALIDOS = 30


def calcular_baseline(execucoes):
    """Baseline PROVISÓRIO a partir de execuções reais coletadas na calibração.

    Mesmo cálculo do Período A (percentis do RTT médio e do jitter das execuções),
    mas com uma janela de minutos em vez de 7 dias, e com um piso nos limites para
    que a resolução do relógio do ping (1 ms no Windows) não gere falso alarme.
    """
    com_rtt = [e for e in execucoes if e["avg"] is not None]
    if len(com_rtt) < MIN_RTT_VALIDOS:
        raise ValueError(f"Só {len(com_rtt)} execuções com RTT válido (mínimo {MIN_RTT_VALIDOS}). "
                         "Confira se o IP responde ping.")
    rtt = np.array([e["avg"] for e in com_rtt])
    jit = np.array([e["jitter"] for e in com_rtt])
    med = float(np.median(rtt))
    piso = max(1.0, 0.05 * med)
    p95 = max(float(np.percentile(rtt, 95)), med + piso)
    p99 = max(float(np.percentile(rtt, 99)), p95 + piso)
    return {
        "mediana_rtt_A": med,
        "p95_rtt_A": p95,
        "p99_rtt_A": p99,
        "mediana_jitter_A": float(np.median(jit)),
        "p95_jitter_A": max(float(np.percentile(jit, 95)), 0.5),
        "ttl_baseline": float(Counter(e["ttl"] for e in com_rtt).most_common(1)[0][0]),
        "n_execucoes": len(execucoes),
        "perda_media_pct": float(np.mean([e["perda"] for e in execucoes])),
    }
