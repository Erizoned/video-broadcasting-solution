import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/StreamCard.css';

function StreamCard({ stream }) {
  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  return (
    <Link to={`/streams/${stream.id}`} className="stream-card">
      <div className="stream-thumbnail">
        <img src={stream.thumbnailUrl} alt={stream.title} />
        {stream.isLive && <span className="live-badge">LIVE</span>}
        <div className="stream-status">
          <span className={`status-indicator ${stream.status}`}>
            {stream.status === 'running' ? 'Live' : 'Offline'}
          </span>
        </div>
      </div>
      <div className="stream-info">
        <div className="streamer-info">
          <img src={stream.streamerAvatar} alt={stream.streamerName} className="streamer-avatar" />
          <div className="stream-details">
            <h3 className="stream-title">{stream.title}</h3>
            <p className="streamer-name">{stream.streamerName}</p>
          </div>
        </div>
        <div className="stream-meta">
          <div className="meta-item">
            <span className="meta-label">Viewers</span>
            <span className="meta-value">{stream.viewersCount}</span>
          </div>
          {stream.status === 'running' && (
            <>
              <div className="meta-item">
                <span className="meta-label">Upload</span>
                <span className="meta-value">{formatBytes(stream.bytesSent)}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Download</span>
                <span className="meta-value">{formatBytes(stream.bytesReceived)}</span>
              </div>
            </>
          )}
        </div>
        {stream.tracks.length > 0 && (
          <div className="stream-tracks">
            {stream.tracks.map((track, index) => (
              <span key={index} className="track-badge">{track}</span>
            ))}
          </div>
        )}
      </div>
    </Link>
  );
}

export default StreamCard; 