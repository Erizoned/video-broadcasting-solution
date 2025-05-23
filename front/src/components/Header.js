import React from 'react';
import { Link } from 'react-router-dom';
import logo from '../assets/VBS_logo.png';
import '../styles/Header.css';

function Header() {
  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">
        <img src={logo} alt="Video Broadcast Logo" className="site-logo" />
      </Link>
      <div className="nav-links">
        <Link to="/">Home</Link>
        <Link to="/features">Features</Link>
      </div>
    </nav>
  );
}

export default Header; 