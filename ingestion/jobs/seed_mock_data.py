"""
Gera dados simulados realistas de posições de ônibus para São Paulo.
Usado enquanto o token SPTrans não está disponível.
Padrões embutidos: pico manhã/tarde, variação por dia da semana, impacto de chuva.
"""
import json
import logging
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import text

from ..db import connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

LINHAS = [
    {"cl": 34041, "lt0": "477A-10", "tp": "TERM. BANDEIRA",    "ts": "TERM. LAPA",         "sl": 1},
    {"cl": 34042, "lt0": "477A-10", "tp": "TERM. LAPA",        "ts": "TERM. BANDEIRA",     "sl": 2},
    {"cl": 33138, "lt0": "875A-10", "tp": "TERM. CAMPO LIMPO", "ts": "CONSOLAÇÃO",         "sl": 1},
    {"cl": 33139, "lt0": "875A-10", "tp": "CONSOLAÇÃO",        "ts": "TERM. CAMPO LIMPO",  "sl": 2},
    {"cl": 36041, "lt0": "8012-10", "tp": "TERM. PINHEIROS",   "ts": "TERM. SANTO AMARO",  "sl": 1},
    {"cl": 36042, "lt0": "8012-10", "tp": "TERM. SANTO AMARO", "ts": "TERM. PINHEIROS",    "sl": 2},
    {"cl": 37711, "lt0": "5100-10", "tp": "TERM. SÃO MATEUS",  "ts": "PRAÇA DA SÉ",        "sl": 1},
    {"cl": 37712, "lt0": "5100-10", "tp": "PRAÇA DA SÉ",       "ts": "TERM. SÃO MATEUS",   "sl": 2},
    {"cl": 39500, "lt0": "6450-10", "tp": "TERM. TUCURUVI",    "ts": "PRAÇA DA SÉ",        "sl": 1},
    {"cl": 39501, "lt0": "6450-10", "tp": "PRAÇA DA SÉ",       "ts": "TERM. TUCURUVI",     "sl": 2},
    {"cl": 40001, "lt0": "3781-10", "tp": "TERM. PENHA",       "ts": "PRAÇA DA SÉ",        "sl": 1},
    {"cl": 40002, "lt0": "3781-10", "tp": "PRAÇA DA SÉ",       "ts": "TERM. PENHA",        "sl": 2},
]

ROTAS = {
    34041: [(-23.5489, -46.6388), (-23.5232, -46.6930)],
    34042: [(-23.5232, -46.6930), (-23.5489, -46.6388)],
    33138: [(-23.6602, -46.7401), (-23.5539, -46.6595)],
    33139: [(-23.5539, -46.6595), (-23.6602, -46.7401)],
    36041: [(-23.5671, -46.6970), (-23.6540, -46.7170)],
    36042: [(-23.6540, -46.7170), (-23.5671, -46.6970)],
    37711: [(-23.6308, -46.4490), (-23.5505, -46.6333)],
    37712: [(-23.5505, -46.6333), (-23.6308, -46.4490)],
    39500: [(-23.4738, -46.6127), (-23.5505, -46.6333)],
    39501: [(-23.5505, -46.6333), (-23.4738, -46.6127)],
    40001: [(-23.5249, -46.5330), (-23.5505, -46.6333)],
    40002: [(-23.5505, -46.6333), (-23.5249, -46.5330)],
}

N_VEICULOS = 15  # por linha


def _frota_ativa(hora: int, dia_semana: int) -> float:
    eh_util = dia_semana not in (0, 6)
    if hora < 5:               return 0.05
    if 6 <= hora <= 9:         return 1.0 if eh_util else 0.5
    if 10 <= hora <= 16:       return 0.6 if eh_util else 0.45
    if 17 <= hora <= 20:       return 0.95 if eh_util else 0.55
    if 21 <= hora <= 22:       return 0.4
    return 0.1


def _velocidade(hora: int, dia_semana: int, precip: float) -> float:
    eh_util = dia_semana not in (0, 6)
    if 6 <= hora <= 9 and eh_util:    base = random.gauss(18, 4)
    elif 17 <= hora <= 20 and eh_util: base = random.gauss(16, 5)
    elif not eh_util:                  base = random.gauss(28, 5)
    else:                              base = random.gauss(24, 4)
    if precip > 10:   base *= random.uniform(0.65, 0.75)
    elif precip > 2.5: base *= random.uniform(0.80, 0.90)
    elif precip > 0:   base *= random.uniform(0.92, 0.98)
    return max(5.0, min(60.0, base))


def seed_linhas() -> None:
    rows = [
        {
            "codigo_linha": l["cl"], "circular": False, "letreiro": l["lt0"],
            "sentido": l["sl"], "tipo": 10,
            "denominacao_terminal_principal": l["tp"],
            "denominacao_terminal_secundario": l["ts"],
            "raw_payload": json.dumps(l),
        }
        for l in LINHAS
    ]
    with connection() as conn:
        conn.execute(text("""
            INSERT INTO raw.olho_vivo_linhas
                (codigo_linha,circular,letreiro,sentido,tipo,
                 denominacao_terminal_principal,denominacao_terminal_secundario,raw_payload)
            VALUES
                (:codigo_linha,:circular,:letreiro,:sentido,:tipo,
                 :denominacao_terminal_principal,:denominacao_terminal_secundario,:raw_payload)
            ON CONFLICT DO NOTHING
        """), rows)
    logger.info("Inseridas %d linhas", len(rows))


def seed_posicoes(dias: int = 5, intervalo_min: int = 30) -> int:
    INSERT = text("""
        INSERT INTO raw.olho_vivo_posicoes
            (coletado_em,hora_referencia,codigo_linha,prefixo_veiculo,
             latitude,longitude,acessivel,raw_payload)
        VALUES
            (:coletado_em,:hora_referencia,:codigo_linha,:prefixo_veiculo,
             :latitude,:longitude,:acessivel,:raw_payload)
    """)

    now   = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = now - timedelta(days=dias)

    # Gera padrão de chuva para o período
    chuva: dict[int, float] = {}
    t = start
    while t < now:
        if random.random() < 0.15:
            chuva[int(t.timestamp())] = random.expovariate(0.3)
        t += timedelta(hours=1)

    total  = 0
    batch  = []
    ts     = start

    while ts < now:
        hora    = ts.hour
        dia_sem = ts.weekday()
        frota   = _frota_ativa(hora, dia_sem)
        precip  = chuva.get(int(ts.replace(minute=0, second=0).timestamp()), 0.0)

        for linha in LINHAS:
            cl     = linha["cl"]
            n_atv  = max(1, int(N_VEICULOS * frota))
            rota   = ROTAS.get(cl, [(-23.55, -46.63), (-23.50, -46.60)])

            for i in range(n_atv):
                prefixo   = f"{cl % 1000:03d}{i:02d}"
                progresso = ((int(ts.timestamp()) // 60 + hash(prefixo)) % 60) / 60.0
                lat = rota[0][0] + (rota[1][0] - rota[0][0]) * progresso + random.gauss(0, 0.002)
                lon = rota[0][1] + (rota[1][1] - rota[0][1]) * progresso + random.gauss(0, 0.002)
                vel = _velocidade(hora, dia_sem, precip)

                batch.append({
                    "coletado_em":    ts,
                    "hora_referencia": ts,
                    "codigo_linha":   cl,
                    "prefixo_veiculo": prefixo,
                    "latitude":       round(lat, 7),
                    "longitude":      round(lon, 7),
                    "acessivel":      random.random() > 0.3,
                    "raw_payload":    json.dumps({"p": prefixo, "py": round(lat,7),
                                                  "px": round(lon,7), "vel_sim": round(vel,1)}),
                })

        # Insere em lotes de 20k para minimizar round-trips
        if len(batch) >= 20000:
            with connection() as conn:
                conn.execute(INSERT, batch)
            total += len(batch)
            logger.info("Inseridos %d registros  (até %s)", total, ts.strftime("%Y-%m-%d %H:%M"))
            batch = []

        ts += timedelta(minutes=intervalo_min)

    if batch:
        with connection() as conn:
            conn.execute(INSERT, batch)
        total += len(batch)

    logger.info("Seed concluído: %d registros de posições", total)
    return total


def run(dias: int = 5) -> None:
    logger.info("Seed de dados simulados — %d dias, intervalo 30min", dias)
    seed_linhas()
    seed_posicoes(dias=dias, intervalo_min=30)


if __name__ == "__main__":
    run()
