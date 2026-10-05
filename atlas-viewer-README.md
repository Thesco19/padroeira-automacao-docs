# Atlas GEV Viewer & Perplexica Integration (Fase 2)

## Arquitetura Geral
O ecossistema **Projeto Atlas + Perplexica** atua como um hub central de inteligência espacial e conceitual. A arquitetura segue o pipeline headless:

```text
Fontes Externas (USGS Sismos, CelesTrak SGP4, OpenSky Voos, Wikipedia Geosearch)
       │
       ▼
Motor GEV Atlas Core (@lab/atlas) & Rota Perplexica (/api/atlas)
       │
       ▼
Payload Canônico GeoJSON (FeatureCollection)
       │
       ▼
Atlas Viewer 2D (Leaflet / CartoDB Dark Matter — Leve, 100% Keyless)
```

## Endpoints da API (`/api/atlas`)
A rota `/api/atlas` no Perplexica expõe os dados normalizados em formato GeoJSON:
- **Parâmetros:**
  - `layers`: Camadas a consultar (ex: `earthquakes,satellites,flights`).
  - `lat`, `lon`: Centro da área de interesse para escopo espacial (radius).
  - `radius`: Raio em quilômetros.
- **Resposta:** `FeatureCollection` contendo propriedades completas, timestamps, proveniência e resumos conceituais da Wikipedia.

## Módulos Reutilizados do GEV (God's Eye View)
- `analystEngine.js`: Motor de consulta e filtros espaciais.
- `orbit/sgp4.js`: Propagador orbital local com `satellite.js` (cálculo de órbita e passagens da ISS e satélites).
- `sources/usgs.js`, `sources/celestrak.js`, `sources/opensky.js`: Coletores keyless de dados em tempo real.
