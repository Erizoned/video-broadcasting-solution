import React, { useEffect, useRef } from 'react';

const JSMpegPlayer = ({ wsUrl }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    let player;
    console.log('JSMpeg:', window.JSMpeg, 'wsUrl:', wsUrl, 'canvas:', canvasRef.current);
    if (window.JSMpeg) {
      player = new window.JSMpeg.Player(wsUrl, {
        canvas: canvasRef.current,
        autoplay: true,
        audio: false,
      });
    } else {
      console.error('JSMpeg is not loaded!');
    }
    return () => {
      if (player) player.destroy();
    };
  }, [wsUrl]);

  return <canvas ref={canvasRef} width={1280} height={720} style={{background: '#000'}} />;
};

const FFmpegStreamPage = () => {
  return (
    <div style={{padding: 32}}>
      <h1>FFmpeg WebSocket Stream Player</h1>
      <JSMpegPlayer wsUrl="ws://127.0.0.1:8082" />
      <div style={{marginTop: 24, color: '#888', fontSize: 14}}>
        <b>Инструкция:</b><br/>
        1. Запусти relay:<br/>
        <code>node websocket-relay.js supersecret 9999 8082</code><br/>
        2. Запусти ffmpeg:<br/>
        <code>ffmpeg -i rtsp://localhost:8554/live/sample1 -f mpegts http://127.0.0.1:9999/supersecret</code><br/>
        3. Открой эту страницу.<br/>
        <b>Важно:</b> В <code>public/index.html</code> должен быть подключён jsmpeg.min.js.<br/>
        <b>WebSocket URL:</b> <code>ws://127.0.0.1:8082</code>
      </div>
    </div>
  );
};

export default FFmpegStreamPage; 