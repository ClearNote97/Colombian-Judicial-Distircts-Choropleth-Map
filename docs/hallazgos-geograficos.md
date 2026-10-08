# Hallazgos geográficos — la geografía judicial ≠ la división político-administrativa

> El corazón del proyecto: el mapa judicial de Colombia **no coincide** con la división
> político-administrativa (departamentos/municipios). Estos hallazgos, emergidos del cruce
> del Mapa Judicial (Rama Judicial) con DIVIPOLA (DANE), lo demuestran con datos.

## 1. Distritos judiciales que cruzan fronteras departamentales

Municipios cuyo **distrito judicial** pertenece a un **departamento distinto** al del municipio.
Notablemente, **el propio PDF de la Rama Judicial los marca** con un sufijo entre paréntesis
(`(BOY)`, `(CESAR)`, `(CUND)`, `(CH)`, `(CAUCA)`) — es decir, la institución reconoce el cruce.

| Distrito judicial | Municipio | Departamento real (DANE) | Marca en el PDF |
|---|---|---|---|
| Arauca | Cubará | Boyacá (15223) | `(BOY)` |
| Bogotá | La Calera | Cundinamarca (25377) | — |
| Buga | San José del Palmar | Chocó (27660) | `(CH)` |
| Cúcuta | González | Cesar (20310) | `(CESAR)` |
| Cúcuta | Río de Oro | Cesar (20614) | `(CESAR)` |
| Cundinamarca | Leticia | Amazonas (91001) | — |
| Cundinamarca | Puerto Nariño | Amazonas (91540) | — |
| Ibagué | Beltrán | Cundinamarca (25086) | `(CUND)` |
| Manizales | Puerto Salgar | Cundinamarca (25572) | `(CUND)` |
| Manizales | Puerto Boyacá | Boyacá (15572) | — |
| Mocoa | Piamonte | Cauca (19533) | `(CAUCA)` |
| Yopal | Pajarito | Boyacá (15518) | — |

### Caso extremo: el distrito de Villavicencio
El distrito judicial de **Villavicencio** abarca municipios de **seis** departamentos distintos:
**Meta, Vichada, Guainía, Guaviare, Vaupés** y algunos de **Cundinamarca** (Medina, Paratebueno,
Guayabetal). Un solo distrito judicial cubre buena parte de la Orinoquía y Amazonía.

## 2. Varios distritos judiciales dentro de un mismo departamento

La subdivisión judicial es, en algunos departamentos, **más fina** que la departamental:
- **Antioquia (05):** distritos *Antioquia* y *Medellín*.
- **Boyacá (15):** distritos *Tunja* y *Santa Rosa de Viterbo*.
- **Santander (68):** distritos *Bucaramanga* y *San Gil*.
- **Valle del Cauca (76):** distritos *Cali* y *Buga*.
- **Norte de Santander (54):** distritos *Cúcuta* y *Pamplona*.

## 3. Municipios judiciales que son corregimientos (sin municipio DANE propio)

Entradas del Mapa Judicial que **no son municipios DANE** sino corregimientos; comparten el
polígono de su municipio: 
- **Santa Rita** → corregimiento de **Cumaribo** (Vichada, 99773) desde 1996.
- **Coconuco** → cabecera/corregimiento de **Puracé** (Cauca, 19585).

## 4. Vacíos del mapa: municipios sin juzgado

Los espacios en blanco del mapa son el hallazgo original del autor: **no todos los municipios
tienen juzgado**. Cuantificado con datos (MGN DANE 2024 vs Mapa Judicial), hay **20 municipios
con territorio que NO aparecen en el Mapa Judicial** (sin juzgado asignado):

| Departamento | # | Nota |
|---|---|---|
| Amazonas | 9 | Áreas remotas / corregimientos departamentales sin juzgado municipal |
| Guainía | 4 | Orinoquía/Amazonía |
| Vaupés | 3 | Amazonía |
| Córdoba | 2 | |
| Bolívar | 1 | **Norosí (13490)** — municipio reciente del sur de Bolívar |
| Cauca | 1 | |

> **Importante — dos tipos de blanco distintos:**
> - **Sin juzgado (20):** tienen geometría pero no están en el Mapa Judicial → brecha de cobertura
>   judicial (el hallazgo). En el mapa se ven como vacíos dentro del contorno del país.
> - **Sin geometría (1):** *Belén de Bajirá (27493)* sí está en el Mapa Judicial, pero el MGN aún no
>   trae su polígono (municipio nuevo en disputa territorial Antioquia/Chocó). Es ausencia de dato
>   cartográfico, no de juzgado.

Por eso el mapa dibuja la **figura completa de Colombia** en gris de fondo: para que estos vacíos se
lean como *municipios sin cobertura dentro del país*, no como ausencia total de territorio.

---

> Fuente de los códigos: DIVIPOLA DANE (junio 2026). Fuente de la jerarquía judicial:
> PDF del Mapa Judicial de la Rama Judicial. Homologación: ver `docs/bitacora-decisiones.md` (D-004).
