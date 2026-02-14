import React, { useState } from 'react';
import MapDashboard from './MapDashboard';
import Sidebar from './Sidebar';
import axios from 'axios';
import './App.css';

function App() {
  const [points, setPoints] = useState({ start: null, end: null });
  const [routes, setRoutes] = useState({ clean: null, fast: null });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRoutes = async (start, end) => {
    setLoading(true);
    setError(null);
    try {
      // Parallel requests for speed
      const requests = [
        axios.post('http://localhost:8000/route', {
          start_lon: start.lng, start_lat: start.lat,
          end_lon: end.lng, end_lat: end.lat,
          mode: 'clean'
        }),
        axios.post('http://localhost:8000/route', {
          start_lon: start.lng, start_lat: start.lat,
          end_lon: end.lng, end_lat: end.lat,
          mode: 'fast'
        })
      ];

      const [cleanRes, fastRes] = await Promise.all(requests);

      setRoutes({
        clean: cleanRes.data,
        fast: fastRes.data
      });

    } catch (err) {
      console.error(err);
      if (err.response && err.response.status === 404) {
        setError("Route not found. Try moving points closer to main roads.");
      } else {
        setError("Server error. Please check backend connection.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleMapClick = (evt) => {
    const { lng, lat } = evt.lngLat;

    // Logic: 
    // 0 points -> Set Start
    // 1 point -> Set End & Fetch
    // 2 points -> Reset & Set Start

    if (!points.start) {
      setPoints({ ...points, start: { lng, lat } });
      setError(null);
    } else if (!points.end) {
      setPoints({ ...points, end: { lng, lat } });
      fetchRoutes(points.start, { lng, lat });
    } else {
      // Reset
      setPoints({ start: { lng, lat }, end: null });
      setRoutes({ clean: null, fast: null });
      setError(null);
    }
  };

  const handleReset = () => {
    setPoints({ start: null, end: null });
    setRoutes({ clean: null, fast: null });
    setError(null);
  };

  return (
    <div className="app-container">
      <Sidebar
        points={points}
        routes={routes}
        loading={loading}
        error={error}
        onReset={handleReset}
      />
      <div style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0, zIndex: 0 }}>
        <MapDashboard
          points={points}
          routes={routes}
          onMapClick={handleMapClick}
        />
      </div>
    </div>
  );
}

export default App;
