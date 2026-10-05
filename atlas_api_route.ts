import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const layersParam = searchParams.get('layers') || 'earthquakes,satellites,flights';
    const lat = parseFloat(searchParams.get('lat') || '-23.55');
    const lon = parseFloat(searchParams.get('lon') || '-46.63');
    const radiusKm = parseFloat(searchParams.get('radius') || '1000');
    const wikiQuery = searchParams.get('wikipedia_query');

    // Dynamic import of @lab/atlas backend
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
      viewContext: { lat, lon, viewRadiusKm: radiusKm },
    });

    await atlas.refreshAll();

    const layerList = layersParam.split(',').map(l => l.trim());
    const features: any[] = [];
    const creditsSet = new Set();

    for (const layer of layerList) {
      const queryResult = await atlas.handleOsintQuery({
        layers: [layer],
        scope: {
          kind: 'radius',
          center: { lat, lon },
          km: radiusKm,
        },
        limit: 25,
      });

      if (queryResult && queryResult.items) {
        queryResult.items.forEach((item: any) => {
          features.push({
            type: 'Feature',
            geometry: item.geometry || { type: 'Point', coordinates: [lon, lat, 0] },
            properties: {
              id: item.id || `${layer}-${Math.random()}`,
              source: item.layerKey || layer,
              category: item.category || layer,
              title: item.properties?.title || `${layer.toUpperCase()} Entity`,
              timestamp: item.properties?.timestamp || new Date().toISOString(),
              magnitude: item.properties?.magnitude,
              depth: item.properties?.depth,
              velocity: item.properties?.velocity,
              altitude: item.properties?.altitude,
              metadata: item.properties || {},
            },
          });
        });
      }
    }

    // Wikipedia integration (geosearch & query)
    try {
      const geoUrl = `https://en.wikipedia.org/w/api.php?action=query&list=geosearch&gscoord=${lat}|${lon}&gsradius=10000&format=json&origin=*`;
      const geoRes = await fetch(geoUrl, { headers: { Accept: 'application/json' } });
      const geoData = await geoRes.json();
      const places = geoData?.query?.geosearch || [];

      for (const place of places.slice(0, 5)) {
        features.push({
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [place.lon, place.lat, 0],
          },
          properties: {
            id: `wiki-${place.pageid}`,
            source: 'wikipedia',
            category: 'poi',
            title: place.title,
            extract: `Wikipedia Geosearch landmark near coordinates (${place.dist}m away).`,
            timestamp: new Date().toISOString(),
            metadata: { url: `https://en.wikipedia.org/wiki/${encodeURIComponent(place.title)}` },
          },
        });
      }
    } catch (wikiErr) {
      console.error('Wikipedia integration error in API:', wikiErr);
    }

    const featureCollection = {
      type: 'FeatureCollection',
      features,
      provenance: {
        engine: 'Atlas GEV + Perplexica',
        timestamp: new Date().toISOString(),
        status: 'live',
      },
    };

    return NextResponse.json(featureCollection, { status: 200 });
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || String(err), type: 'FeatureCollection', features: [] },
      { status: 500 }
    );
  }
}
