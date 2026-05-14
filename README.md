# 🚌 Observatório de Mobilidade Urbana de São Paulo

> Plataforma analítica end-to-end que cruza pontualidade da frota de ônibus,
> clima e geografia para responder perguntas sobre mobilidade em SP.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)]()
[![dbt](https://img.shields.io/badge/dbt-1.8-orange.svg)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39-red.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Autor:** Gabriel Barbosa Galvão Ribeiro

---

## 🎯 Sobre

São Paulo tem 12+ milhões de habitantes e mais de 1.300 linhas de ônibus operando
diariamente. Apesar dos dados públicos disponíveis, não existe uma plataforma analítica
acessível que cruze pontualidade, clima, geografia e tráfego.

Este projeto coleta dados em tempo real da API Olho Vivo (SPTrans) e do Open-Meteo,
transforma-os com dbt em um modelo dimensional e os expõe via dashboard interativo no
Streamlit Cloud — respondendo perguntas como:

- Quais linhas têm maior variabilidade de tempo de viagem?
- Como o clima impacta a pontualidade por região?
- Quais corredores concentram maior risco de incidentes?

---

## 📈 Demo

🔗 **[Dashboard ao vivo](https://seu-app.streamlit.app)** ← _atualizar após deploy_

---

## 🏗️ Arquitetura

```
SPTrans API      Open-Meteo
     │                │
     └──── GitHub Actions (cron 15min) ────┐
                                           ▼
                                 PostgreSQL / Neon
                                  schema: raw
                                           │
                                    dbt (cron 06h)
                                  staging → marts
                                           │
                              ┌────────────┼────────────┐
                          Streamlit                 Power BI
                           Cloud                   Desktop
```

| Camada        | Tecnologia                        |
|---------------|-----------------------------------|
| Ingestão      | Python · httpx · tenacity         |
| Storage       | PostgreSQL (Neon — free tier)     |
| Transformação | dbt-core 1.8 + dbt-postgres       |
| Dashboard     | Streamlit · Plotly · Folium       |
| Relatório     | Power BI Desktop                  |
| Orquestração  | GitHub Actions                    |

---

## 📊 Insights Destacados

> _Serão preenchidos após coleta de 2+ semanas de dados._

1. **[Em breve]** Linhas com maior dispersão de velocidade no pico da manhã
2. **[Em breve]** Correlação precipitação × velocidade média (r = ?)
3. **[Em breve]** Horário com maior degradação de pontualidade

---

## 🚀 Executar localmente

### Pré-requisitos

- Python 3.11+
- PostgreSQL (ou conta Neon gratuita)
- Token SPTrans Olho Vivo ([instruções](docs/fontes-de-dados.md#sptrans))

### Setup

```bash
# 1. Clone o repositório
git clone https://github.com/FeshowBiel/observatorio-mobilidade-sp.git
cd observatorio-mobilidade-sp

# 2. Crie o ambiente virtual
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements-dev.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com seu token SPTrans e URL do banco

# 5. Crie as tabelas no banco
psql $DATABASE_URL -f ingestion/sql/001_create_schemas.sql
psql $DATABASE_URL -f ingestion/sql/002_create_raw_tables.sql

# 6. Rode a primeira coleta
python -m ingestion.jobs.ingest_olho_vivo
python -m ingestion.jobs.ingest_weather

# 7. Configure o dbt
cp dbt/profiles.yml.template ~/.dbt/profiles.yml
# Edite ~/.dbt/profiles.yml com suas credenciais

# 8. Execute os models dbt
cd dbt && dbt deps && dbt run && dbt test

# 9. Suba o dashboard
streamlit run dashboard/app.py
```

---

## 📂 Estrutura

```
observatorio-mobilidade-sp/
├── .github/workflows/     # GitHub Actions (ingestão + dbt)
├── ingestion/             # Scripts Python de coleta (ETL)
│   ├── jobs/              # Jobs individuais por fonte
│   └── sql/               # DDLs das tabelas raw
├── dbt/                   # Projeto dbt (staging → marts)
│   └── models/
│       ├── staging/       # Views de limpeza
│       ├── intermediate/  # Cálculos intermediários
│       └── marts/         # Tabelas analíticas finais
├── dashboard/             # App Streamlit (4 páginas)
├── notebooks/             # Análise exploratória (EDA)
├── powerbi/               # Relatório .pbix
├── docs/                  # Documentação e ADRs
└── tests/                 # Testes unitários Python
```

---

## 🧪 Decisões Técnicas

Veja [`docs/decisoes-tecnicas.md`](docs/decisoes-tecnicas.md) para os ADRs do projeto.

---

## 📝 Licença

MIT © Gabriel Barbosa Galvão Ribeiro
