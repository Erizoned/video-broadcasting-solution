import React, { useState, useEffect } from 'react';
import StreamCard from './StreamCard';
import '../styles/StreamGrid.css';

function StreamGrid() {
  const [streams, setStreams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  // Simulate fetching streams
  const fetchStreams = async () => {
    setLoading(true);
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Simulate stream data - now only 6 streams per page
    const newStreams = Array(6).fill(null).map((_, index) => ({
      id: `stream-${page}-${index}`,
      title: `Amazing Stream ${page}-${index}`,
      streamerName: `Streamer${index}`,
      category: 'Gaming',
      viewerCount: Math.floor(Math.random() * 10000),
      thumbnailUrl: `https://picsum.photos/seed/${page}-${index}/400/225`,
      streamerAvatar: `https://picsum.photos/seed/avatar-${index}/50/50`
    }));

    setStreams(prev => [...prev, ...newStreams]);
    setLoading(false);
    // Simulate end of content after 2 pages
    if (page >= 2) setHasMore(false);
  };

  useEffect(() => {
    fetchStreams();
  }, [page]);

  const handleLoadMore = () => {
    if (!loading && hasMore) {
      setPage(prev => prev + 1);
    }
  };

  return (
    <div className="stream-grid-container">
      <div className="stream-grid">
        {streams.map(stream => (
          <StreamCard key={stream.id} stream={stream} />
        ))}
        {loading && Array(6).fill(null).map((_, index) => (
          <StreamCard key={`loading-${index}`} isLoading={true} />
        ))}
      </div>
      <div className="load-more-container">
        {hasMore ? (
          <button 
            className="load-more-btn" 
            onClick={handleLoadMore}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Load More'}
          </button>
        ) : (
          <div className="end-of-content">
            No more streams to load
          </div>
        )}
      </div>
    </div>
  );
}

export default StreamGrid; 