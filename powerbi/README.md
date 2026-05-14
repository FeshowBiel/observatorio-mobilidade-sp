# Power BI — Relatório Executivo

## Como conectar ao banco Neon

1. Abra o **Power BI Desktop**
2. **Obter Dados → Banco de Dados PostgreSQL**
3. **Servidor:** `<host>.neon.tech` (veja sua string de conexão no painel do Neon)
4. **Banco de dados:** `observatorio`
5. **Modo de conectividade:** Import (para snapshot) ou DirectQuery (para dados em tempo real)
6. Navegue até o schema `marts` e importe as tabelas:
   - `mart_pontualidade_diaria`
   - `mart_correlacao_clima`
   - `fct_viagens`
   - `dim_linha`
   - `dim_tempo`

## Estrutura sugerida do relatório

| Página | Título | Visuais |
|--------|--------|---------|
| 1 | Visão Geral | KPI cards, tabela de top linhas |
| 2 | Pontualidade | Linha temporal, heatmap por hora/dia |
| 3 | Clima | Scatter chuva x velocidade, segmentação |
| 4 | Mapa | Mapa de calor por região |

## Publicar o .pbix no repo

Após criar o relatório:
```
File → Save As → powerbi/observatorio.pbix
git add powerbi/observatorio.pbix
git commit -m "feat: adiciona relatório Power BI"
```

> ⚠️ O arquivo `.pbix` contém credenciais de conexão. Certifique-se de usar
> credenciais somente-leitura ou remover a string de conexão antes de commitar.
