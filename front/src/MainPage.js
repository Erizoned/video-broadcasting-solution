import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import HeroPattern from './components/HeroPattern';
import './styles/MainPage.css';

function formatBytes(bytes) {
  if (bytes === undefined || bytes === null) return '-';
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

function formatTime(iso) {
  if (!iso) return '-';
  const d = new Date(iso);
  return d.toLocaleString();
}

function safeTrackLabel(track) {
  if (!track) return '—';
  if (typeof track === 'string') return track;
  if (typeof track === 'object') {
    if (track.type) return track.type;
    return JSON.stringify(track);
  }
  return String(track);
}

function StreamCardRelevant({ stream }) {
  const statusColor = stream.status === 'running' ? '#4ade80' : '#f87171'; // green-400 / red-400
  const statusBg = stream.status === 'running' ? 'rgba(74,222,128,0.12)' : 'rgba(248,113,113,0.12)';
  return (
    <div style={{
      background: '#fff',
      borderRadius: 16,
      boxShadow: '0 2px 16px 0 #0001',
      padding: 24,
      margin: '18px 0',
      color: '#23272f',
      display: 'flex',
      flexDirection: 'column',
      gap: 12,
      border: `1.5px solid ${statusBg}`,
      transition: 'border 0.2s',
      maxWidth: 700,
      marginLeft: 'auto',
      marginRight: 'auto',
    }}>
      <div style={{display: 'flex', alignItems: 'center', gap: 14}}>
        <i className="fas fa-broadcast-tower" style={{color: statusColor, fontSize: 22, marginRight: 8}}/>
        <span style={{fontWeight: 700, fontSize: 20, letterSpacing: 0.5}}>{stream.stream_key}</span>
        <span style={{
          background: statusBg, color: statusColor, borderRadius: 8, padding: '2px 12px', marginLeft: 10,
          fontWeight: 600, fontSize: 13, letterSpacing: 1, border: `1px solid ${statusColor}`
        }}>{stream.status === 'running' ? 'Live' : 'Stopped'}</span>
        <span style={{marginLeft: 'auto', fontSize: 13, color: '#6b7280'}}>Source: <span style={{color:'#23272f'}}>{typeof stream.source === 'string' ? stream.source : '-'}</span></span>
      </div>
      <div style={{display: 'flex', gap: 32, flexWrap: 'wrap', marginTop: 8}}>
        <div style={{minWidth: 120}}>
          <div style={{fontSize: 13, color: '#6b7280'}}>Bytes Received</div>
          <div style={{fontWeight: 600, fontSize: 16}}>{formatBytes(stream.bytes_received)}</div>
        </div>
        <div style={{minWidth: 120}}>
          <div style={{fontSize: 13, color: '#6b7280'}}>Bytes Sent</div>
          <div style={{fontWeight: 600, fontSize: 16}}>{formatBytes(stream.bytes_sent)}</div>
        </div>
        <div style={{minWidth: 100}}>
          <div style={{fontSize: 13, color: '#6b7280'}}>Viewers</div>
          <div style={{fontWeight: 600, fontSize: 16}}><i className="fas fa-user-friends" style={{marginRight: 6, color:'#60a5fa'}}/> {stream.readers_count}</div>
        </div>
        <div style={{minWidth: 120}}>
          <div style={{fontSize: 13, color: '#6b7280'}}>Tracks</div>
          <div style={{fontWeight: 600, fontSize: 16, display:'flex', gap:6, flexWrap:'wrap'}}>
            {Array.isArray(stream.tracks) && stream.tracks.length > 0
              ? stream.tracks.map((t, i) => (
                  <span key={i} style={{
                    background: '#f3f4f6', color: '#23272f', borderRadius: 6, padding: '2px 8px', fontSize: 13, fontWeight: 500, border: '1px solid #e5e7eb'
                  }}>{safeTrackLabel(t)}</span>
                ))
              : <span style={{color:'#9ca3af'}}>—</span>}
          </div>
        </div>
        <div style={{minWidth: 120}}>
          <div style={{fontSize: 13, color: '#6b7280'}}>Protocols</div>
          <div style={{fontWeight: 600, fontSize: 16, display:'flex', gap:6, flexWrap:'wrap'}}>
            {stream.protocol_counts && typeof stream.protocol_counts === 'object' && Object.keys(stream.protocol_counts).length > 0
              ? Object.entries(stream.protocol_counts).map(([proto, count]) => (
                  <span key={proto} style={{
                    background: '#f3f4f6', color: '#23272f', borderRadius: 6, padding: '2px 8px', fontSize: 13, fontWeight: 500, border: '1px solid #e5e7eb'
                  }}>{proto}: {count}</span>
                ))
              : <span style={{color:'#9ca3af'}}>—</span>}
          </div>
        </div>
        <div style={{minWidth: 180}}>
          <div style={{fontSize: 13, color: '#6b7280'}}>Started</div>
          <div style={{fontWeight: 600, fontSize: 15}}>{formatTime(stream.ready_time)}</div>
        </div>
      </div>
    </div>
  );
}

function MainPage() {
  const [streams, setStreams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStreams = async () => {
      try {
        const response = await fetch('http://localhost:8001/streams');
        const data = await response.json();
        setStreams(data.streams || []);
        setLoading(false);
      } catch (err) {
        setError('Ошибка загрузки стримов');
        setLoading(false);
      }
    };
    fetchStreams();
  }, []);

  return (
    <div className="main-page">
      <Header />
      
      {/* Hero Section */}
      <section className="hero">
        <HeroPattern />
        <div className="hero-content">
          <h1>Professional Video Broadcasting Made Simple</h1>
          <p>Stream your content to millions with our powerful broadcasting platform. Start your journey today!</p>
          <div className="hero-buttons">
            <button className="primary-btn">Start Streaming</button>
            <button className="secondary-btn">Watch Streams</button>
          </div>
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-number">10M+</span>
              <span className="stat-label">Active Viewers</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">50K+</span>
              <span className="stat-label">Active Streamers</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">99.9%</span>
              <span className="stat-label">Uptime</span>
            </div>
          </div>
        </div>
      </section>

      {/* Live Streams Section */}
      <section className="live-streams">
        <div className="section-header">
          <div className="section-title">
            <h2>Live Streams</h2>
            <span className="live-indicator">LIVE</span>
          </div>
        </div>
        {loading ? (
          <div className="loading-state">Загрузка стримов...</div>
        ) : error ? (
          <div className="error-state">{error}</div>
        ) : (
          <div style={{marginTop: 18}}>
            {streams.length === 0 ? (
              <div style={{color:'#6b7280', fontSize: 18, textAlign:'center', margin: 24}}>Нет активных стримов</div>
            ) : (
              streams.map((stream) => (
                <StreamCardRelevant key={stream.stream_key} stream={stream} />
              ))
            )}
          </div>
        )}
      </section>

      {/* Features Section */}
      <section className="features" id="features">
        <div className="section-header">
          <h2>Why Choose Us</h2>
          <p className="section-subtitle">Everything you need to start your streaming journey</p>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <i className="fas fa-video"></i>
            </div>
            <h3>High-Quality Streaming</h3>
            <p>Broadcast in up to 4K resolution with minimal latency and adaptive bitrate streaming</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <i className="fas fa-globe"></i>
            </div>
            <h3>Global Reach</h3>
            <p>Reach viewers worldwide with our distributed network and low-latency CDN</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <i className="fas fa-chart-line"></i>
            </div>
            <h3>Advanced Analytics</h3>
            <p>Track viewer engagement, stream performance, and audience demographics in real-time</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <i className="fas fa-shield-alt"></i>
            </div>
            <h3>Secure Platform</h3>
            <p>Enterprise-grade security with DDoS protection and content encryption</p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works">
        <div className="section-header">
          <h2>How It Works</h2>
          <p className="section-subtitle">Start streaming in three simple steps</p>
        </div>
        <div className="steps-container">
          <div className="step-card">
            <div className="step-number">1</div>
            <h3>Create Account</h3>
            <p>Sign up in minutes and set up your streaming profile</p>
          </div>
          <div className="step-card">
            <div className="step-number">2</div>
            <h3>Configure Stream</h3>
            <p>Set up your stream settings and customize your channel</p>
          </div>
          <div className="step-card">
            <div className="step-number">3</div>
            <h3>Go Live</h3>
            <p>Start broadcasting to your audience instantly</p>
          </div>
        </div>
      </section>
      <Footer />
    </div>
  );
}

export default MainPage;