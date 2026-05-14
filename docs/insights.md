# Insights do Observatório

> Este documento será preenchido após pelo menos 2 semanas de coleta contínua.
> Estrutura preparada para registrar os achados analíticos.

---

## Insight 1 — [Título]

**Pergunta:** _Qual linha tem maior variabilidade de velocidade no pico da manhã?_

**Dado/Cálculo:**
```sql
select letreiro, stddev(velocidade_kmh) as variabilidade
from marts.fct_viagens
where hora_do_dia between 7 and 9
group by letreiro
order by variabilidade desc
limit 10;
```

**Resultado:** _A ser preenchido_

**E daí?** _A ser preenchido_

---

## Insight 2 — [Título]

**Pergunta:** _Existe correlação entre precipitação e velocidade média?_

**Dado/Cálculo:** Correlação de Pearson entre `precipitacao_mm` e `velocidade_media_kmh` no `mart_correlacao_clima`.

**Resultado:** _A ser preenchido_

**E daí?** _A ser preenchido_

---

## Insight 3 — [Título]

**Pergunta:** _Qual a diferença de velocidade média entre dias úteis e fins de semana?_

**Resultado:** _A ser preenchido_

---

## Template para novos insights

```markdown
## Insight N — [Título curto e chamativo]

**Pergunta:** _O que você queria descobrir?_

**Dado/Cálculo:** _Query SQL ou cálculo Python usado_

**Resultado:** _O número/fato descoberto. Seja específico: "A linha X tem 2,3x mais variabilidade..."_

**Visualização:** ![screenshot](../notebooks/img/insight_N.png)

**E daí?** _Por que isso importa para o usuário de ônibus, gestor público ou seguradora?_
```
