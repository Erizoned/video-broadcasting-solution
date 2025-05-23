import React from 'react';
import patternSvg from '../assets/pattern.svg';

function HeroPattern() {
  return (
    <div 
      className="hero-overlay"
      style={{
        backgroundImage: `url(${patternSvg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        opacity: 0.1
      }}
    />
  );
}

export default HeroPattern; 