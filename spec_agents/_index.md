# Roster de agentes — índice maestro (ClearNote_Py_DA · Análisis de datos)

Roster **adaptado a plantilla de datos** (propagado desde `ClearNote_Dev`). Aquí domina la **familia de datos**;
el núcleo de app no aplica. El *cómo* del formato y la materialización está en [`README.md`](./README.md).

> **Activación bajo demanda:** el `lead-architect` decide qué agentes se materializan según el trabajo real;
> no todos por defecto.

## Coordinación

| Agente | Rol | `model_hint` | Herramientas |
|---|---|---|---|
| [`lead-architect`](./lead-architect.yaml) | Decide el roster activo + custodia la coherencia. Compuerta de cierre. | `frontier` | read, grep, glob |
| [`analytics-lead`](./analytics-lead.yaml) | Coordina el pipeline de datos y enmarca la pregunta analítica. | `frontier` | read, grep, glob |

## Familia de datos (el núcleo de esta plantilla) — pipeline por fases

Flujo: **ingesta → limpieza → stats/ML → visualización → reporte** (esta plantilla es **no-SQL**).

| Agente | Fase / rol | `model_hint` | Herramientas |
|---|---|---|---|
| [`data-ingestor`](./data-ingestor.yaml) | Adquiere datos a la capa cruda (inmutable). | `balanced` | read, grep, glob, edit, write, bash, web |
| [`data-cleaner`](./data-cleaner.yaml) | Limpia/normaliza/valida (pandas; `src/utils`). | `balanced` | read, grep, glob, edit, write, bash |
| [`stats-analyst`](./stats-analyst.yaml) | EDA, métricas y pruebas estadísticas, con rigor. | `frontier` | read, grep, glob, edit, write, bash |
| [`ml-engineer`](./ml-engineer.yaml) | Modelado ML reproducible, sin leakage. | `frontier` | read, grep, glob, edit, write, bash |
| [`viz-specialist`](./viz-specialist.yaml) | Visuales analíticos claros, accesibles y honestos. | `balanced` | read, grep, glob, edit, write, bash |
| [`insight-reporter`](./insight-reporter.yaml) | Traduce resultados a hallazgos accionables (negocio). | `balanced` | read, grep, glob, write, edit |

## Investigación académica (opt-in)

| Agente | Propósito | `model_hint` | Herramientas |
|---|---|---|---|
| [`literature-reviewer`](./literature-reviewer.yaml) | Buscar, leer y sintetizar fuentes con citas trazables. | `frontier` | read, grep, glob, web |
| [`academic-writer`](./academic-writer.yaml) | Redactar el manuscrito y la investigación en `docs/`. | `frontier` | read, grep, glob, write, edit |

## Núcleo transversal (aplica a cualquier trabajo)

| Agente | Propósito | `model_hint` | Herramientas |
|---|---|---|---|
| [`test-writer`](./test-writer.yaml) | Tests (test-first): happy + edge + vacío. | `balanced` | read, grep, glob, write, edit, bash |
| [`code-reviewer`](./code-reviewer.yaml) | Calidad, bugs, performance — gate pre-cierre. | `balanced` | read, grep, glob |
| [`security-auditor`](./security-auditor.yaml) | Manejo de secretos, privacidad/PII de los datos. | `frontier` | read, grep, glob |
| [`doc-writer`](./doc-writer.yaml) | Mantener `docs/` y el diccionario de datos en sync. | `balanced` | read, grep, glob, edit, write |

> **Si esta plantilla llegara a consultar un motor SQL**, súmale `sql-analyst` desde `ClearNote_Py_DA_SQL`.
