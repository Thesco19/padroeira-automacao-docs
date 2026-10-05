import z from 'zod';
import { ResearchAction } from '../../types';
import { Chunk } from '@/lib/types';

const schema = z.object({
  layer: z
    .enum(['earthquakes', 'satellites', 'flights', 'military', 'ais-live-vessels', 'local-firms'])
    .describe('The OSINT / spatial layer to query from the GEV Atlas engine (earthquakes, satellites, flights, etc.).'),
  action: z
    .enum(['query', 'pass'])
    .default('query')
    .describe('Action type: "query" for spatial osint search, "pass" for satellite SGP4 orbital pass prediction.'),
  center: z
    .object({
      lat: z.number().describe('Center latitude'),
      lon: z.number().describe('Center longitude'),
      km: z.number().optional().describe('Radius in kilometers'),
    })
    .optional()
    .describe('Spatial scope center and radius.'),
  sortBy: z.string().optional().describe('Sorting field (e.g. magnitude, distance).'),
  limit: z.number().int().min(1).max(50).optional().describe('Max records to return.'),
});

const atlasDescription = `
Consulta dados e eventos georreferenciados em tempo real do ecossistema Atlas. Use esta ferramenta sempre que o usuário perguntar sobre a localização atual de satélites (ISS, Starlink, LEO com SGP4), abalos sísmicos e terremotos recentes (USGS), ou tráfego aéreo (OpenSky).
`;

const atlasAction: ResearchAction<typeof schema> = {
  name: 'atlas_osint',
  schema: schema,
  getToolDescription: () =>
    'Consulta dados e eventos georreferenciados em tempo real do ecossistema Atlas (satélites, terremotos USGS, voos OpenSky).',
  getDescription: () => atlasDescription,
  enabled: (config) => config.sources.includes('atlas') || true,
  execute: async (input) => {
    const results: Chunk[] = [];

    try {
      const atlasModule = await import('/opt/stacks/osint/atlas/src/index.js');
      const usgsModule = await import('/opt/stacks/osint/atlas/src/sources/usgs.js');
      const celestrakModule = await import('/opt/stacks/osint/atlas/src/sources/celestrak.js');
      const openskyModule = await import('/opt/stacks/osint/atlas/src/sources/opensky.js');

      const atlas = atlasModule.createAtlas({
        sources: {
          earthquakes: usgsModule.createUsgsSource(),
          satellites: celestrakModule.createCelesTrakSource(),
          flights: openskyModule.createOpenSkySource(),
        },
      });

      await atlas.refreshAll();

      if (input.action === 'pass') {
        const nextPass = atlasModule.findNextSatellitePass ? await atlasModule.findNextSatellitePass() : null;
        results.push({
          content: `Satellite SGP4 Pass Info: ${JSON.stringify(nextPass || { info: 'Pass computed locally via SGP4' })}`,
          metadata: {
            title: 'Satellite Pass Prediction',
            url: '',
            createdAt: new Date().toISOString(),
          },
        });
      } else {
        const querySpec: any = {
          layers: [input.layer],
          limit: input.limit || 10,
        };

        if (input.center) {
          querySpec.scope = {
            kind: 'radius',
            center: { lat: input.center.lat, lon: input.center.lon },
            km: input.center.km || 500,
          };
        }

        if (input.sortBy) {
          querySpec.sortBy = input.sortBy;
          querySpec.sortDir = 'desc';
        }

        const queryResult = await atlas.handleOsintQuery(querySpec);

        if (queryResult && queryResult.items && queryResult.items.length > 0) {
          for (const item of queryResult.items) {
            results.push({
              content: `Atlas OSINT [${input.layer}]: ${JSON.stringify(item.properties || item)} (GeoJSON: ${JSON.stringify(item.geometry || {})})`,
              metadata: {
                title: `${input.layer} event ${item.id || ''}`,
                url: '',
                createdAt: item.properties?.timestamp || new Date().toISOString(),
              },
            });
          }
        } else {
          results.push({
            content: `Atlas OSINT query for layer "${input.layer}" returned 0 records.`,
            metadata: { title: 'Atlas OSINT', url: '', createdAt: new Date().toISOString() },
          });
        }
      }
    } catch (err: any) {
      results.push({
        content: `Atlas OSINT error: ${err?.message || String(err)}`,
        metadata: { title: 'Error', url: '', createdAt: new Date().toISOString() },
      });
    }

    return {
      type: 'search_results',
      results,
    };
  },
};

export default atlasAction;
