import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Footer.css';

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <h4>VideoBroadcast</h4>
          <p>Professional video streaming platform</p>
        </div>
        <div className="footer-section">
          <h4>Quick Links</h4>
          <Link to="/">Home</Link>
        </div>
        <div className="footer-section">
          <h4>Contact</h4>
          <p>support@videobroadcast.com</p>
          <p>+1 (555) 123-4567</p>
        </div>
      </div>
      <div className="footer-bottom">
        <p>&copy; {new Date().getFullYear()} VideoBroadcast. All rights reserved.</p>
      </div>
    </footer>
  );
}

export default Footer; 