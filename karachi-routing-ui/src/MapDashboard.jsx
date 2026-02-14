import React, { useState } from 'react';
import Map, { Source, Layer, Marker } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

export default function MapDashboard({ points, routes, onMapClick }) {
  const [viewState, setViewState] = useState({
    longitude: 67.0011,
    latitude: 24.8607,
    zoom: 12
  });

  // Layer Styles
  const fastLayer = {
    id: 'fast-route',
    type: 'line',
    paint: {
      'line-color': '#d93025', // Google Red
      'line-width': 5,
      'line-opacity': 0.7
    }
  };

  const cleanLayer = {
    id: 'clean-route',
    type: 'line',
    paint: {
      'line-color': '#188038', // Google Green
      'line-width': 7,
      'line-opacity': 1
    }
  };

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <Map
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        style={{ width: '100%', height: '100%' }}
        mapStyle="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json" // Light Mode!
        onClick={onMapClick}
        cursor={points.start && points.end ? 'auto' : 'crosshair'}
      >
        {/* Render Markers */}
        {points.start && <Marker longitude={points.start.lng} latitude={points.start.lat} color="#1e8e3e" />}
        {points.end && <Marker longitude={points.end.lng} latitude={points.end.lat} color="#d93025" />}

        {/* Render Routes */}
        {routes.fast && (
          <Source id="fast" type="geojson" data={routes.fast}>
            <Layer {...fastLayer} />
          </Source>
        )}

        {routes.clean && (
          <Source id="clean" type="geojson" data={routes.clean}>
            <Layer {...cleanLayer} />
          </Source>
        )}
      </Map>
    </div>
  );
}
