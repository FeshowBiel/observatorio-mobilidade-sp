# Catálogo de Fontes de Dados

## Perguntas de negócio

1. **Pontualidade:** quais linhas têm a maior dispersão (desvio padrão) no tempo médio entre paradas em horário de pico?
2. **Clima:** existe correlação estatística entre precipitação (mm/h) e velocidade média por linha na região central?
3. **Geografia:** quais regiões da cidade concentram maior densidade de ônibus lentos em hora de pico?
4. **Operacional:** qual a variação de velocidade média por corredor em dias úteis vs sábados?
5. **Temporal:** qual o "pico do pico" — horário com maior degradação de pontualidade?

---

## SPTrans Olho Vivo

- **URL base:** `http://api.olhovivo.sptrans.com.br/v2.1/`
- **Auth:** POST em `/Login/Autenticar?token={TOKEN}` — retorna cookie de sessão
- **Rate limit:** não documentado; coleta a cada 60–90s é segura
- **Formato:** JSON
- **Frequência de coleta:** a cada 15 minutos (via GitHub Actions)
- **Volumetria estimada:** ~8.000–12.000 posições por coleta (~800k registros/dia)

### Endpoints principais

| Endpoint | Descrição |
|----------|-----------|
| `POST /Login/Autenticar?token=...` | Autenticação |
| `GET /Posicao` | Posições de todos os veículos |
| `GET /Posicao/Linha?codigoLinha={id}` | Posições de uma linha |
| `GET /Linha/Buscar?termosBusca={query}` | Busca de linhas |
| `GET /Previsao?codigoParada=...` | Previsão de chegada |
| `GET /Corredor` | Lista de corredores |

### Como obter o token

1. Acesse https://www.sptrans.com.br/desenvolvedores/
2. Crie uma conta e faça login
3. Vá em **Meus Aplicativos → Adicionar novo aplicativo**
4. Copie o token gerado e cole no `.env` como `SPTRANS_TOKEN`

### Schema do endpoint `/Posicao`

```json
{
  "hr": "18:32:00",
  "l": [
    {
      "c": "NOME DA LINHA",
      "cl": 34041,       // código da linha
      "sl": 1,           // sentido
      "lt0": "477A-10",
      "lt1": "TERM. BANDEIRA",
      "qv": 22,          // qtd veículos
      "vs": [
        {
          "p": "12345",  // prefixo do veículo
          "a": true,     // acessível
          "ta": "18:31:55",
          "py": -23.5505, // latitude
          "px": -46.6333  // longitude
        }
      ]
    }
  ]
}
```

### Notas

- O campo `hr` é apenas hora (HH:MM:SS), sem data — usar data do servidor na inserção
- Veículos em garagem não aparecem na resposta
- O cookie de sessão expira; o cliente implementa re-autenticação automática

---

## Open-Meteo

- **URL forecast:** `https://api.open-meteo.com/v1/forecast`
- **URL histórico:** `https://archive-api.open-meteo.com/v1/archive`
- **Auth:** não requer token
- **Custo:** gratuito para uso não-comercial
- **Frequência de coleta:** a cada 15 min (UPSERT — idempotente)
- **Volumetria estimada:** ~48 linhas/dia (dados horários)

### Variáveis coletadas

| Variável | Descrição | Unidade |
|----------|-----------|---------|
| `temperature_2m` | Temperatura a 2m | °C |
| `precipitation` | Precipitação acumulada | mm/h |
| `wind_speed_10m` | Velocidade do vento | km/h |
| `weathercode` | Código WMO do tempo | — |

### Categorização de chuva (calculada no dbt)

| Categoria | Critério |
|-----------|----------|
| `sem_chuva` | precipitação = 0 mm/h |
| `chuva_fraca` | < 2,5 mm/h |
| `chuva_moderada` | 2,5–10 mm/h |
| `chuva_forte` | > 10 mm/h |

---

## GeoSampa

- **URL:** https://geosampa.prefeitura.sp.gov.br
- **Formato:** Shapefile, GeoJSON
- **Auth:** não requer token
- **Frequência:** download único (dados estáticos)

### Datasets relevantes

| Dataset | O que usar |
|---------|-----------|
| Distritos | Polígonos dos 96 distritos de SP |
| Subprefeituras | Agrupamento de distritos |
| Eixos viários | Rede de ruas para geocodificação |

### Como usar

```python
import geopandas as gpd
distritos = gpd.read_file("docs/geo/distritos_sp.geojson")
```

---

## CET-SP (v2 — pós-MVP)

- **Opção 1:** Dados Abertos do Município → http://dados.prefeitura.sp.gov.br/
- **Opção 2:** Scraping de boletins de ocorrências (CET-SP publica PDFs)
- **Status:** adiado para v2 do projeto

---

## Notas sobre volumetria e retenção

Com coleta a cada 15 min e ~10.000 posições/coleta:

| Período | Registros estimados | Tamanho estimado |
|---------|---------------------|-----------------|
| 1 dia   | ~960.000            | ~200 MB         |
| 7 dias  | ~6.7 M              | ~1.4 GB         |
| 30 dias | ~29 M               | ~6 GB           |

**Política de retenção:** deletar `raw.olho_vivo_posicoes` com `coletado_em < NOW() - INTERVAL '60 days'` para manter dentro do free tier do Neon (0,5 GB). Os dados agregados nos marts são retidos permanentemente.
