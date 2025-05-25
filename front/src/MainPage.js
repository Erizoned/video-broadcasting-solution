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
      maxWidth: 1000,
      minWidth: 900,
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
      <div style={{display: 'flex', gap: 32, flexWrap: 'nowrap', marginTop: 8}}>
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
  const [filter, setFilter] = useState('all'); // all | online | offline
  const [sortOrder, setSortOrder] = useState('onlineFirst'); // onlineFirst | offlineFirst | alpha | viewers | startedNew | startedOld | bytesReceived | bytesSent | bytesSentMin

  useEffect(() => {
    let intervalId;
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
    intervalId = setInterval(fetchStreams, 3000);
    return () => clearInterval(intervalId);
  }, []);

  // Фильтрация по кнопкам
  let filteredStreams = streams;
  if (filter === 'online') {
    filteredStreams = filteredStreams.filter(s => s.status === 'running');
  } else if (filter === 'offline') {
    filteredStreams = filteredStreams.filter(s => s.status !== 'running');
  }

  // Сортировка по выбранному порядку
  let sortedStreams = [...filteredStreams];
  if (sortOrder === 'onlineFirst') {
    sortedStreams.sort((a, b) => (b.status === 'running') - (a.status === 'running'));
  } else if (sortOrder === 'offlineFirst') {
    sortedStreams.sort((a, b) => (a.status === 'running') - (b.status === 'running'));
  } else if (sortOrder === 'alpha') {
    sortedStreams.sort((a, b) => a.stream_key.localeCompare(b.stream_key));
  } else if (sortOrder === 'viewers') {
    sortedStreams.sort((a, b) => (b.readers_count || 0) - (a.readers_count || 0));
  } else if (sortOrder === 'startedNew') {
    sortedStreams.sort((a, b) => {
      const ta = a.ready_time ? new Date(a.ready_time).getTime() : 0;
      const tb = b.ready_time ? new Date(b.ready_time).getTime() : 0;
      return tb - ta;
    });
  } else if (sortOrder === 'startedOld') {
    sortedStreams.sort((a, b) => {
      const ta = a.ready_time ? new Date(a.ready_time).getTime() : 0;
      const tb = b.ready_time ? new Date(b.ready_time).getTime() : 0;
      return ta - tb;
    });
  } else if (sortOrder === 'bytesReceived') {
    sortedStreams.sort((a, b) => (b.bytes_received || 0) - (a.bytes_received || 0));
  } else if (sortOrder === 'bytesSent') {
    sortedStreams.sort((a, b) => (b.bytes_sent || 0) - (a.bytes_sent || 0));
  } else if (sortOrder === 'bytesSentMin') {
    sortedStreams.sort((a, b) => (a.bytes_sent || 0) - (b.bytes_sent || 0));
  }

  return (
    <div className="main-page">
      <Header />
      
      {/* Hero Section */}
      <section className="hero">
        <HeroPattern />
        <div className="hero-content">
          <h1>Professional Video Broadcasting Made Simple</h1>
          <p>Stream your content to millions with our powerful broadcasting platform. <br/> Start your journey today!</p>
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
        {/* Фильтры */}
        <div style={{display:'flex', gap:12, margin:'18px 0 10px 0', justifyContent:'center', alignItems:'center'}}>
          <button
            onClick={() => setFilter('all')}
            style={{
              background: filter==='all' ? '#4ade80' : '#f3f4f6',
              color: filter==='all' ? '#fff' : '#23272f',
              border: 'none',
              borderRadius: 8,
              padding: '6px 18px',
              fontWeight: 600,
              fontSize: 15,
              boxShadow: filter==='all' ? '0 2px 8px #4ade8033' : 'none',
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >Все</button>
          <button
            onClick={() => setFilter('online')}
            style={{
              background: filter==='online' ? '#60a5fa' : '#f3f4f6',
              color: filter==='online' ? '#fff' : '#23272f',
              border: 'none',
              borderRadius: 8,
              padding: '6px 18px',
              fontWeight: 600,
              fontSize: 15,
              boxShadow: filter==='online' ? '0 2px 8px #60a5fa33' : 'none',
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >Только онлайн</button>
          <button
            onClick={() => setFilter('offline')}
            style={{
              background: filter==='offline' ? '#f87171' : '#f3f4f6',
              color: filter==='offline' ? '#fff' : '#23272f',
              border: 'none',
              borderRadius: 8,
              padding: '6px 18px',
              fontWeight: 600,
              fontSize: 15,
              boxShadow: filter==='offline' ? '0 2px 8px #f8717133' : 'none',
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >Только оффлайн</button>
          <select
            value={sortOrder}
            onChange={e => setSortOrder(e.target.value)}
            style={{
              marginLeft: 24,
              padding: '6px 14px',
              borderRadius: 8,
              border: '1.5px solid #e5e7eb',
              fontWeight: 600,
              fontSize: 15,
              color: '#23272f',
              background: '#f9fafb',
              cursor: 'pointer',
              outline: 'none',
              boxShadow: 'none',
              transition: 'border 0.15s',
            }}
          >
            <option value="onlineFirst">Онлайн сверху</option>
            <option value="offlineFirst">Оффлайн сверху</option>
            <option value="alpha">По алфавиту</option>
            <option value="viewers">По зрителям</option>
            <option value="startedNew">По дате старта (новые)</option>
            <option value="startedOld">По дате старта (старые)</option>
            <option value="bytesReceived">По полученным байтам</option>
            <option value="bytesSent">По отправленным байтам (max)</option>
            <option value="bytesSentMin">По отправленным байтам (min)</option>
          </select>
        </div>
        {loading ? (
          <div className="loading-state">Загрузка стримов...</div>
        ) : error ? (
          <div className="error-state">{error}</div>
        ) : (
          <div style={{marginTop: 18}}>
            {sortedStreams.length === 0 ? (
              <div style={{color:'#6b7280', fontSize: 18, textAlign:'center', margin: 24}}>Нет активных стримов</div>
            ) : (
              sortedStreams.map((stream) => (
                <StreamCardRelevant key={stream.stream_key} stream={stream} />
              ))
            )}
          </div>
        )}
      </section>
      <Footer />
    </div>
  );
}

export default MainPage;