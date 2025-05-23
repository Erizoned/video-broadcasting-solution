import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/StreamCard.css';

function StreamCard({ stream, isLoading }) {
  if (isLoading) {
    return (
      <div className="stream-card loading">
        <div className="stream-thumbnail-placeholder"></div>
        <div className="stream-info">
          <div className="streamer-avatar-placeholder"></div>
          <div className="stream-details-placeholder">
            <div className="stream-title-placeholder"></div>
            <div className="streamer-name-placeholder"></div>
            <div className="stream-category-placeholder"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Link to={`/stream/${stream.id}`} className="stream-card">
      <div className="stream-thumbnail">
        <img src={stream.thumbnailUrl} alt={stream.title} />
      </div>
      <div className="stream-info">
        <div className="streamer-avatar">
          <img src={stream.streamerAvatar} alt={stream.streamerName} />
        </div>
        <div className="stream-details">
          <h3 className="stream-title">{stream.title}</h3>
          <p className="streamer-name">{stream.streamerName}</p>
        </div>
      </div>
    </Link>
  );
}

export default StreamCard; 