import React from 'react';
import { Leaf, Clock, Zap, MapPin } from 'lucide-react';

export default function Sidebar({ points, routes, loading, error, onReset }) {
    const cleanNodes = routes.clean?.metadata?.nodes_visited || 0;
    const fastNodes = routes.fast?.metadata?.nodes_visited || 0;

    // Simulated stats for "Impact"
    const pollutionSaved = cleanNodes > 0 ? Math.round((cleanNodes * 0.4) + (Math.random() * 10)) : 0; // Fake AQI points for demo
    const timeAdded = cleanNodes > 0 ? Math.round((cleanNodes * 0.05)) : 0; // Fake minutes

    return (
        <div className="sidebar">
            <div className="header">
                <h1>
                    Tri-P
                    <span style={{ fontSize: '0.8rem', background: '#e8f0fe', color: '#1a73e8', padding: '2px 8px', borderRadius: '12px' }}>BETA</span>
                </h1>
                <p>Eco-Routing for Karachi</p>
            </div>

            <div className="status-panel">
                <div className="status-step">
                    <MapPin size={20} color={points.start ? "#1e8e3e" : "#bdc1c6"} />
                    <span style={{ fontWeight: points.start ? 500 : 400 }}>
                        {points.start ? "Start Selected" : "Choose starting point"}
                    </span>
                </div>
                <div className="line"></div>
                <div className="status-step">
                    <MapPin size={20} color={points.end ? "#d93025" : "#bdc1c6"} />
                    <span style={{ fontWeight: points.end ? 500 : 400 }}>
                        {points.end ? "Destination Selected" : "Choose destination"}
                    </span>
                </div>
            </div>

            {error && (
                <div className="error-card">
                    <div className="error-icon">⚠️</div>
                    <div className="error-text">{error}</div>
                </div>
            )}

            {loading && (
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Calculating safest path...</p>
                </div>
            )}

            {routes.clean && !loading && (
                <div className="results-panel">
                    <h3>Route Comparison</h3>

                    <div className="card clean-card">
                        <div className="card-header">
                            <Leaf size={20} />
                            <span>Clean Route</span>
                        </div>
                        <div className="card-stat">
                            <span className="value">{cleanNodes}</span>
                            <span className="label">Nodes</span>
                        </div>
                        <div className="card-badge">RECOMMENDED</div>
                    </div>

                    <div className="card fast-card">
                        <div className="card-header">
                            <Zap size={20} />
                            <span>Fast Route</span>
                        </div>
                        <div className="card-stat">
                            <span className="value">{fastNodes}</span>
                            <span className="label">Nodes</span>
                        </div>
                    </div>

                    <div className="impact-box">
                        <h4>Your Impact</h4>
                        <div className="impact-row">
                            <span>📉 Pollution Exposure</span>
                            <span className="green">-{pollutionSaved}%</span>
                        </div>
                        <div className="impact-row">
                            <span>⏱️ Time Impact</span>
                            <span className="orange">+{timeAdded} min</span>
                        </div>
                    </div>

                    <button className="reset-btn" onClick={onReset}>
                        Clear Route
                    </button>
                </div>
            )}
        </div>
    );
}
