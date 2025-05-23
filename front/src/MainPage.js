import React from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import StreamGrid from './components/StreamGrid';
import './styles/MainPage.css';

function MainPage() {
  return (
    <div className="main-page">
      <Header />
      
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1>Professional Video Broadcasting Made Simple</h1>
          <p>Stream your content to millions with our powerful broadcasting platform</p>
          <div className="hero-buttons">
            <button className="secondary-btn">Watch Streams</button>
          </div>
        </div>
      </section>

      {/* Live Streams Section */}
      <section className="live-streams">
        <div className="section-header">
          <h2>Live Streams</h2>
          <div className="stream-filters">
            <button className="filter-btn active">All</button>
            <button className="filter-btn">Gaming</button>
            <button className="filter-btn">Music</button>
            <button className="filter-btn">Just Chatting</button>
          </div>
        </div>
        <StreamGrid />
      </section>

      {/* Features Section */}
      <section className="features" id="features">
        <h2>Why Choose Us</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🎥</div>
            <h3>High-Quality Streaming</h3>
            <p>Broadcast in up to 4K resolution with minimal latency</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🌐</div>
            <h3>Global Reach</h3>
            <p>Reach viewers worldwide with our distributed network</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Analytics</h3>
            <p>Track viewer engagement and stream performance</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔒</div>
            <h3>Secure Platform</h3>
            <p>Enterprise-grade security for your content</p>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

export default MainPage;