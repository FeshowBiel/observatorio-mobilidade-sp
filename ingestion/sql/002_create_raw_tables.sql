-- Posições GPS dos ônibus (alta volumetria)
CREATE TABLE IF NOT EXISTS raw.olho_vivo_posicoes (
    id              BIGSERIAL PRIMARY KEY,
    coletado_em     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    hora_referencia TIMESTAMPTZ NOT NULL,
    codigo_linha    INT         NOT NULL,
    prefixo_veiculo VARCHAR(10),
    latitude        NUMERIC(10, 7),
    longitude       NUMERIC(10, 7),
    acessivel       BOOLEAN,
    raw_payload     JSONB       NOT NULL
);

CREATE INDEX idx_posicoes_coletado_em ON raw.olho_vivo_posicoes (coletado_em);
CREATE INDEX idx_posicoes_linha       ON raw.olho_vivo_posicoes (codigo_linha);
CREATE INDEX idx_posicoes_veiculo     ON raw.olho_vivo_posicoes (prefixo_veiculo);

-- Cadastro de linhas (baixa frequência: 1x/dia)
CREATE TABLE IF NOT EXISTS raw.olho_vivo_linhas (
    id                               BIGSERIAL PRIMARY KEY,
    coletado_em                      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    codigo_linha                     INT          NOT NULL,
    circular                         BOOLEAN,
    letreiro                         VARCHAR(20),
    sentido                          SMALLINT,
    tipo                             SMALLINT,
    denominacao_terminal_principal   VARCHAR(255),
    denominacao_terminal_secundario  VARCHAR(255),
    raw_payload                      JSONB        NOT NULL
);

-- Clima horário
CREATE TABLE IF NOT EXISTS raw.weather_horario (
    id                  BIGSERIAL PRIMARY KEY,
    coletado_em         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    hora_referencia     TIMESTAMPTZ  NOT NULL UNIQUE,
    latitude            NUMERIC(10, 7),
    longitude           NUMERIC(10, 7),
    temperatura_c       NUMERIC(4, 1),
    precipitacao_mm     NUMERIC(5, 2),
    velocidade_vento_kmh NUMERIC(5, 2),
    raw_payload         JSONB        NOT NULL
);

CREATE INDEX idx_weather_hora ON raw.weather_horario (hora_referencia);
