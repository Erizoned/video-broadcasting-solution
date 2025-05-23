import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import '../styles/StreamPage.css';

function StreamPage() {
  const { streamId } = useParams();
  const navigate = useNavigate();
  const [stream, setStream] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching stream data
    const fetchStream = async () => {
      setLoading(true);
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Simulate stream data
      setStream({
        id: streamId,
        title: `Amazing Stream ${streamId}`,
        streamerName: `Streamer${streamId.split('-')[2]}`,
        category: 'Gaming',
        viewerCount: Math.floor(Math.random() * 10000),
        description: 'Welcome to my stream! Join me for some amazing gameplay and fun interactions with the chat.',
        tags: ['Gaming', 'Live', 'Entertainment'],
        streamerAvatar: `https://picsum.photos/seed/avatar-${streamId.split('-')[2]}/200/200`
      });
      setLoading(false);
    };

    fetchStream();
  }, [streamId]);

  if (loading) {
    return (
      <div className="stream-page">
        <Header />
        <div className="stream-container loading">
          <div className="stream-player-placeholder"></div>
          <div className="stream-info-placeholder">
            <div className="stream-title-placeholder"></div>
            <div className="streamer-info-placeholder"></div>
            <div className="stream-description-placeholder"></div>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="stream-page">
      <Header />
      <div className="stream-container">
        <div className="stream-player">
          {/* Здесь будет видео плеер */}
          <div className="video-placeholder">
            <div className="play-button">▶</div>
            <p>Stream Preview</p>
          </div>
        </div>
        
        <div className="stream-info">
          <div className="stream-header">
            <div className="streamer-info">
              <img src={stream.streamerAvatar} alt={stream.streamerName} className="streamer-avatar" />
              <div className="streamer-details">
                <h1>{stream.title}</h1>
                <p className="streamer-name">{stream.streamerName}</p>
                <p className="stream-category">{stream.category}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}

export default StreamPage; 