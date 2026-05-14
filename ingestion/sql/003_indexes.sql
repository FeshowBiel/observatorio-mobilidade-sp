-- Índices adicionais para performance em queries analíticas

-- Particionamento por hora (útil para queries de série temporal)
CREATE INDEX IF NOT EXISTS idx_posicoes_hora_linha
    ON raw.olho_vivo_posicoes (hora_referencia, codigo_linha);

-- Índice geoespacial (requer PostGIS; ignore se não disponível)
-- CREATE INDEX idx_posicoes_geo ON raw.olho_vivo_posicoes
--     USING GIST (ST_MakePoint(longitude, latitude));

-- Índice para deduplicação de linhas
CREATE UNIQUE INDEX IF NOT EXISTS uq_linhas_codigo
    ON raw.olho_vivo_linhas (codigo_linha, sentido);
