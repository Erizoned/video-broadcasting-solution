import React, { useEffect, useState, useRef } from 'react';
import Header from './components/Header';

const LOGS_API = 'http://localhost:8001/logs';

function getLogColor(line) {
  if (/error|exception|fail|traceback/i.test(line)) return '#ef4444'; // красный
  if (/warn/i.test(line)) return '#f59e42'; // оранжевый
  if (/info/i.test(line)) return '#38bdf8'; // голубой
  if (/debug/i.test(line)) return '#a3e635'; // салатовый
  return '#d1d5db'; // светло-серый
}

function LogPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const logEndRef = useRef(null);
  const logBoxRef = useRef(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const userWasAtBottom = useRef(true);

  // Проверка, был ли пользователь внизу
  const isUserAtBottom = () => {
    const el = logBoxRef.current;
    if (!el) return true;
    return el.scrollHeight - el.scrollTop - el.clientHeight < 40; // 40px tolerance
  };

  const fetchLogs = async () => {
    try {
      // Сохраняем, был ли пользователь внизу до обновления
      userWasAtBottom.current = isUserAtBottom();
      const res = await fetch(LOGS_API);
      const data = await res.json();
      setLogs(data.logs || []);
      setLoading(false);
    } catch (e) {
      setError('Ошибка загрузки логов');
      setLoading(false);
    }
  };

  useEffect(() => {
    let intervalId;
    fetchLogs();
    intervalId = setInterval(fetchLogs, 3000);
    return () => clearInterval(intervalId);
  }, []);

  // Автоскролл только если пользователь был внизу до обновления
  useEffect(() => {
    if (autoScroll && userWasAtBottom.current && logBoxRef.current) {
      const el = logBoxRef.current;
      el.scrollTop = el.scrollHeight;
    }
  }, [logs]);

  // Следим за скроллом пользователя
  const handleScroll = () => {
    if (!logBoxRef.current) return;
    if (isUserAtBottom()) {
      setAutoScroll(true);
    } else {
      setAutoScroll(false);
    }
  };

  // Кнопка для скролла вниз
  const scrollToBottom = () => {
    if (logBoxRef.current) {
      logBoxRef.current.scrollTop = logBoxRef.current.scrollHeight;
    }
  };

  return (
    <div style={{minHeight: '100vh', background: '#f3f4f6', marginTop: '80px'}}>
      <Header />
      <div style={{maxWidth: 950, margin: '40px auto', background: '#f9fafb', borderRadius: 16, boxShadow: '0 4px 32px #0002', padding: 0, border: '1.5px solid #e5e7eb'}}>
        <div style={{display:'flex', alignItems:'center', justifyContent:'space-between', padding: '28px 32px 10px 32px', borderBottom: '1.5px solid #e5e7eb'}}>
          <div style={{display:'flex', alignItems:'center', gap:14}}>
            <span style={{fontSize: 32, color:'#38bdf8'}}><i className="fas fa-file-alt"/></span>
            <span style={{fontWeight: 700, fontSize: 28, color: '#23272f', letterSpacing: 0.5}}>Логи конвертера</span>
          </div>
          <div style={{display:'flex', gap:10}}>
          </div>
        </div>
        <div style={{padding: '0 32px 32px 32px'}}>
          {loading ? (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '40px 0',
              color: '#6b7280',
              fontSize: 18,
              gap: 16
            }}>
              <div style={{
                width: 40,
                height: 40,
                border: '3px solid #e5e7eb',
                borderTop: '3px solid #60a5fa',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }}></div>
              <div>Loading logs...</div>
            </div>
          ) : error ? (
            <div style={{color:'#ef4444', fontWeight:600, fontSize:18, margin:'32px 0', textAlign:'center'}}>{error}</div>
          ) : (
            <>
            <div
              ref={logBoxRef}
              onScroll={handleScroll}
              style={{
                background: '#18181b', color: '#d1d5db', fontFamily: 'monospace',
                borderRadius: 10, padding: 18, minHeight: 400, maxHeight: 600, overflowY: 'auto', fontSize: 15,
                boxShadow: '0 2px 12px #0002',
                border: '1.5px solid #23272f',
                transition: 'border 0.2s',
                scrollbarColor: '#38bdf8 #23272f',
                scrollbarWidth: 'thin',
              }}
            >
              {logs.length === 0 ? (
                <div style={{color:'#888'}}>Логи отсутствуют</div>
              ) : (
                logs.map((line, i) => (
                  <div key={i} style={{whiteSpace: 'pre-wrap', color: getLogColor(line), fontWeight: /error|exception|fail/i.test(line) ? 700 : 500}}>{line}</div>
                ))
              )}
              <div ref={logEndRef} />
            </div>
            <div style={{display:'flex', justifyContent:'center', marginTop: 18, gap: 12}}>
              <button
                onClick={scrollToBottom}
                style={{background:'#38bdf8', color:'#fff', border:'none', borderRadius:8, padding:'7px 18px', fontWeight:600, fontSize:15, cursor:'pointer', boxShadow:'0 2px 8px #23272f33', transition:'all 0.15s'}}
              >Scroll Down</button>
            </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default LogPage; 