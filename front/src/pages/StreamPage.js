import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { streamService } from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';
import '../styles/StreamPage.css';

function StreamPage() {
  const { streamName } = useParams();
  const navigate = useNavigate();
  const [stream, setStream] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStreamDetails = async () => {
      try {
        const data = await streamService.getStreamDetails(streamName);
        setStream(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load stream details. Please try again later.');
        setLoading(false);
      }
    };

    fetchStreamDetails();
    // Set up polling for live updates
    const interval = setInterval(fetchStreamDetails, 5000);
    return () => clearInterval(interval);
  }, [streamName]);

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not started';
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <div className="stream-page">
        <Header />
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading stream details...</p>
        </div>
        <Footer />
      </div>
    );
  }

  if (error) {
    return (
      <div className="stream-page">
        <Header />
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/')} className="back-button">
            Return to Home
          </button>
        </div>
        <Footer />
      </div>
    );
  }

  if (!stream) {
    return (
      <div className="stream-page">
        <Header />
        <div className="not-found-container">
          <h2>Stream Not Found</h2>
          <p>The stream you're looking for doesn't exist or has been removed.</p>
          <button onClick={() => navigate('/')} className="back-button">
            Return to Home
          </button>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="stream-page">
      <Header />
      <main className="stream-content">
        <div className="stream-player-container">
          <div className="stream-player">
            <div className="video-placeholder">
              <h3>Stream: {stream.title}</h3>
              <div className="stream-status-badge">
                <span className={`status-indicator ${stream.status}`}>
                  {stream.status === 'running' ? 'LIVE' : 'OFFLINE'}
                </span>
              </div>
              {stream.status === 'running' ? (
                <p>Stream is currently live</p>
              ) : (
                <p>Stream is offline</p>
              )}
            </div>
          </div>
          <div className="stream-info">
            <h1>{stream.title}</h1>
            <div className="streamer-info">
              <img 
                src={stream.streamerAvatar} 
                alt={stream.streamerName} 
                className="streamer-avatar"
              />
              <div className="streamer-details">
                <h2>{stream.streamerName}</h2>
                <span className="category">{stream.category}</span>
              </div>
            </div>
            <div className="stream-stats">
              <div className="stat">
                <span className="stat-label">Status</span>
                <span className={`stat-value status-${stream.status}`}>
                  {stream.status === 'running' ? 'Live' : 'Offline'}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Viewers</span>
                <span className="stat-value">{stream.viewersCount}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Started</span>
                <span className="stat-value">{formatDate(stream.readyTime)}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Upload</span>
                <span className="stat-value">{formatBytes(stream.bytesSent)}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Download</span>
                <span className="stat-value">{formatBytes(stream.bytesReceived)}</span>
              </div>
            </div>
            {stream.tracks.length > 0 && (
              <div className="stream-tracks-section">
                <h3>Stream Tracks</h3>
                <div className="stream-tracks">
                  {stream.tracks.map((track, index) => (
                    <span key={index} className="track-badge">{track}</span>
                  ))}
                </div>
              </div>
            )}
            <div className="stream-description">
              <h3>About this stream</h3>
              <p>{stream.description}</p>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default StreamPage; 