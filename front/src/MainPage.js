import React from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import StreamGrid from './components/StreamGrid';
import HeroPattern from './components/HeroPattern';
import './styles/MainPage.css';

function MainPage() {
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
          <div className="stream-filters">
            <button className="filter-btn active">All</button>
            <button className="filter-btn">Gaming</button>
            <button className="filter-btn">Music</button>
            <button className="filter-btn">Just Chatting</button>
            <button className="filter-btn">Education</button>
          </div>
        </div>
        <StreamGrid />
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