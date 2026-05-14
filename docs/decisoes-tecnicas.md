# Decisões Técnicas (ADRs)

## ADR-01: Neon em vez de Render para PostgreSQL

**Contexto:** O projeto coleta dados continuamente e precisa de um banco que persista além de 30 dias.

**Decisão:** Usar Neon (free permanente, 0,5 GB) em vez de Render (free expira em 30 dias).

**Consequências:** O free tier de 0,5 GB pode ficar pequeno se coletar todas as linhas sem retenção. Mitigação: política de rolling deletion >60 dias na tabela raw de posições. Quando o projeto migrar para Azure (pós-AZ-900), mover para Azure Database for PostgreSQL.

---

## ADR-02: dbt em vez de SQL puro para transformações

**Contexto:** As transformações envolvem múltiplas camadas (staging → intermediate → marts) com dependências entre elas.

**Decisão:** Usar dbt-core com materialização em views (staging/intermediate) e tabelas (marts).

**Consequências:** Curva de aprendizado inicial, mas ganho em testabilidade, documentação automática (`dbt docs`) e reprodutibilidade. Os testes de schema substituem validações manuais.

---

## ADR-03: GitHub Actions em vez de Airflow/Prefect para orquestração

**Contexto:** Projeto de portfólio com orçamento zero e equipe de 1 pessoa.

**Decisão:** GitHub Actions com cron expressions para orquestrar ingestão (15 min) e dbt (diário).

**Consequências:** Limitação de 2.000 min/mês no free tier. Com cron de 15 min = ~2.880 execuções/mês de ~1 min cada = ~2.880 min/mês → risco de estourar. Mitigação: monitorar uso em Settings → Actions e reduzir para 30 min se necessário.

---

## ADR-04: Streamlit Cloud em vez de Heroku/Railway para o dashboard

**Contexto:** Dashboard de dados com visualizações interativas, sem backend customizado.

**Decisão:** Streamlit Cloud (free, deploy direto do GitHub, SSL automático).

**Consequências:** App "dorme" após inatividade e leva ~30s para acordar. Aceitável para portfólio; documentar no README.

---

## ADR-05: Haversine no SQL em vez de PostGIS

**Contexto:** Cálculo de distância entre posições GPS consecutivas para estimar velocidade.

**Decisão:** Implementar fórmula de Haversine diretamente no SQL do model intermediate, sem extensão PostGIS.

**Consequências:** Neon free tier não garante suporte a PostGIS. A fórmula é suficiente para distâncias <50 km com erro <0,1%. Se precisar de análise geoespacial mais rica (buffer, intersect), revisar para usar GeoPandas nos notebooks.

---

## ADR-06: JSONB para raw_payload em vez de colunas separadas

**Contexto:** A API SPTrans pode mudar campos sem aviso.

**Decisão:** Salvar o payload JSON completo em coluna `raw_payload JSONB` além das colunas tipadas extraídas.

**Consequências:** Maior tamanho de armazenamento, mas garante que nenhum dado é descartado na ingestão. Se a API adicionar um campo relevante, basta criar um novo model dbt sem reprocessar histórico.
