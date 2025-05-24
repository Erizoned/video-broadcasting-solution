import React from 'react';
import StreamCard from './StreamCard';
import '../styles/StreamGrid.css';

function StreamGrid({ streams = [] }) {
  if (!streams.length) {
    return (
      <div className="no-streams-message">
        No streams available at the moment
      </div>
    );
  }

  return (
    <div className="stream-grid-container">
      <div className="stream-grid">
        {streams.map(stream => (
          <StreamCard 
            key={stream.id} 
            stream={{
              id: stream.id,
              title: stream.title,
              streamerName: stream.streamerName,
              category: stream.category,
              viewerCount: stream.viewerCount,
              thumbnailUrl: stream.thumbnailUrl,
              streamerAvatar: stream.streamerAvatar
            }} 
          />
        ))}
      </div>
    </div>
  );
}

export default StreamGrid; 