import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Header.css';

function Header() {
  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">VideoBroadcast</Link>
      <div className="nav-links">
        <Link to="/">Home</Link>
        <Link to="/features">Features</Link>
      </div>
    </nav>
  );
}

export default Header; 