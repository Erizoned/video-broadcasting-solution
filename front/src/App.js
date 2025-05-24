import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainPage from './MainPage';
import FFmpegStreamPage from './pages/FFmpegStreamPage';
import './App.css';

function App() {
  console.log('App component rendering');

  return (
    <Router>
<<<<<<< Updated upstream
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/streams/:streamName" element={<StreamPage />} />
      </Routes>
=======
      <div className="App">
        <Routes>
          <Route path="/" element={<MainPage />} />
          <Route path="/ffmpeg-stream" element={<FFmpegStreamPage />} />
        </Routes>
      </div>
>>>>>>> Stashed changes
    </Router>
  );
}

export default App;
