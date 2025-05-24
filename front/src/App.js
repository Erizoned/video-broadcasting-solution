import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainPage from './MainPage';
import StreamPage from './pages/StreamPage';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/streams/:streamName" element={<StreamPage />} />
      </Routes>
    </Router>
  );
}

export default App;
