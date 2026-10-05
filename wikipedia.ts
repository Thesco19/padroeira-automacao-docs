import z from 'zod';
import { ResearchAction } from '../../types';
import { Chunk } from '@/lib/types';

const schema = z.object({
  query: z
    .string()
    .optional()
    .describe('The search query or concept name to look up on Wikipedia (conceptual/historical/entity search).'),
  title: z
    .string()
    .optional()
    .describe('Exact Wikipedia page title to retrieve summary for.'),
  coordinates: z
    .object({
      lat: z.number().describe('Latitude for Wikipedia geosearch'),
      lon: z.number().describe('Longitude for Wikipedia geosearch'),
      radius: z.number().optional().describe('Radius in meters (max 10000) for geosearch'),
    })
    .optional()
    .describe('Geospatial coordinates for Wikipedia geosearch near an OSINT event or location.'),
});

const wikipediaDescription = `
Consulta a API da Wikipedia para resumos conceituais/históricos ou busca pontos de interesse (POIs) e instalações geográficas próximas a um par de coordenadas (latitude, longitude).
`;

const wikipediaAction: ResearchAction<typeof schema> = {
  name: 'wikipedia_search',
  schema: schema,
  getToolDescription: () =>
    'Consulta a API da Wikipedia para resumos conceituais, históricos ou geosearch por coordenadas.',
  getDescription: () => wikipediaDescription,
  enabled: (config) => config.sources.includes('wikipedia') || true,
  execute: async (input) => {
    const results: Chunk[] = [];

    try {
      if (input.coordinates) {
        const lat = input.coordinates.lat;
        const lon = input.coordinates.lon;
        const radius = input.coordinates.radius || 10000;
        const url = `https://en.wikipedia.org/w/api.php?action=query&list=geosearch&gscoord=${lat}|${lon}&gsradius=${radius}&format=json&origin=*`;
        
        const res = await fetch(url, { headers: { Accept: 'application/json' } });
        const data = await res.json();
        const places = data?.query?.geosearch || [];

        for (const place of places.slice(0, 10)) {
          results.push({
            content: `Wikipedia Geosearch Landmark: ${place.title} (dist: ${place.dist}m, lat: ${place.lat}, lon: ${place.lon})`,
            metadata: {
              title: place.title,
              url: `https://en.wikipedia.org/wiki/${encodeURIComponent(place.title)}`,
              createdAt: new Date().toISOString(),
            },
          });
        }
      } else if (input.title) {
        const url = `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(input.title)}`;
        const res = await fetch(url, { headers: { Accept: 'application/json' } });
        const data = await res.json();

        if (data && data.title && data.extract) {
          results.push({
            content: `Wikipedia Summary (${data.title}): ${data.extract}`,
            metadata: {
              title: data.title,
              url: data.content_urls?.desktop?.page || `https://en.wikipedia.org/wiki/${encodeURIComponent(data.title)}`,
              createdAt: new Date().toISOString(),
            },
          });
        }
      } else if (input.query) {
        const searchUrl = `https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(input.query)}&format=json&origin=*`;
        const res = await fetch(searchUrl, { headers: { Accept: 'application/json' } });
        const data = await res.json();
        const searchHits = data?.query?.search || [];

        for (const hit of searchHits.slice(0, 5)) {
          const summaryUrl = `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(hit.title)}`;
          try {
            const sumRes = await fetch(summaryUrl, { headers: { Accept: 'application/json' } });
            const sumData = await sumRes.json();
            if (sumData && sumData.extract) {
              results.push({
                content: `Wikipedia Concept (${sumData.title}): ${sumData.extract}`,
                metadata: {
                  title: sumData.title,
                  url: sumData.content_urls?.desktop?.page || `https://en.wikipedia.org/wiki/${encodeURIComponent(sumData.title)}`,
                  createdAt: new Date().toISOString(),
                },
              });
            }
          } catch {
            results.push({
              content: `Wikipedia Search Hit: ${hit.title} — ${hit.snippet.replace(/<[^>]*>/g, '')}`,
              metadata: {
                title: hit.title,
                url: `https://en.wikipedia.org/wiki/${encodeURIComponent(hit.title)}`,
                createdAt: new Date().toISOString(),
              },
            });
          }
        }
      }

      if (results.length === 0) {
        results.push({
          content: 'No Wikipedia results found for the given query/coordinates.',
          metadata: { title: 'Wikipedia Search', url: '', createdAt: new Date().toISOString() },
        });
      }
    } catch (err: any) {
      results.push({
        content: `Wikipedia search error: ${err?.message || String(err)}`,
        metadata: { title: 'Error', url: '', createdAt: new Date().toISOString() },
      });
    }

    return {
      type: 'search_results',
      results,
    };
  },
};

export default wikipediaAction;
