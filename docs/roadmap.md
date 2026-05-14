# Roadmap de Execução

O roadmap completo do projeto está disponível no arquivo original compartilhado pelo autor.

## Status atual

- [x] Setup inicial do ambiente
- [x] Estrutura do repositório
- [x] Camada de ingestão (SPTrans + Open-Meteo)
- [x] DDLs das tabelas raw
- [x] Projeto dbt com models staging, intermediate e marts
- [x] Dashboard Streamlit (4 páginas)
- [x] GitHub Actions (ingestão + dbt)
- [ ] Banco Neon criado e conectado
- [ ] Token SPTrans configurado no .env
- [ ] 1 semana de dados coletados
- [ ] dbt run completo sem erros
- [ ] Deploy no Streamlit Cloud
- [ ] Notebooks de análise exploratória
- [ ] Power BI (.pbix)
- [ ] README com screenshots reais
- [ ] Posts no LinkedIn

## Próximas etapas imediatas

1. Criar conta no Neon e copiar `DATABASE_URL` para `.env`
2. Obter token SPTrans em https://www.sptrans.com.br/desenvolvedores/
3. Rodar `python -m ingestion.jobs.ingest_olho_vivo` localmente para testar
4. Fazer `git remote add origin` e push para o GitHub
5. Configurar os Secrets no GitHub (Settings → Secrets)
6. Ativar os workflows
