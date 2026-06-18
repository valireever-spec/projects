import React, { useState } from 'react';
import VerificationEngine from './components/intelligence/VerificationEngine';
import PressAnalyzer from './components/intelligence/PressAnalyzer';
import ViralScanner from './components/intelligence/ViralScanner';
import ContentCalendar from './components/production/ContentCalendar';
import ExportPanel from './components/production/ExportPanel';

export default function App() {
  const [activeTab, setActiveTab] = useState('verification');

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <h1 style={styles.title}>The Ignored Signal</h1>
        <p style={styles.tagline}>Content verification & production platform</p>
      </header>

      <nav style={styles.nav}>
        <button
          onClick={() => setActiveTab('verification')}
          style={{
            ...styles.navButton,
            borderBottom: activeTab === 'verification' ? '2px solid #c0392b' : 'none',
            color: activeTab === 'verification' ? '#e9e5da' : '#636077',
          }}
        >
          🔍 Verification Engine
        </button>
        <button
          onClick={() => setActiveTab('press')}
          style={{
            ...styles.navButton,
            borderBottom: activeTab === 'press' ? '2px solid #c0392b' : 'none',
            color: activeTab === 'press' ? '#e9e5da' : '#636077',
          }}
        >
          📰 Press Analyzer
        </button>
        <button
          onClick={() => setActiveTab('viral')}
          style={{
            ...styles.navButton,
            borderBottom: activeTab === 'viral' ? '2px solid #c0392b' : 'none',
            color: activeTab === 'viral' ? '#e9e5da' : '#636077',
          }}
        >
          🔥 Viral Scanner
        </button>
        <button
          onClick={() => setActiveTab('calendar')}
          style={{
            ...styles.navButton,
            borderBottom: activeTab === 'calendar' ? '2px solid #c0392b' : 'none',
            color: activeTab === 'calendar' ? '#e9e5da' : '#636077',
          }}
        >
          📅 Calendar
        </button>
        <button
          onClick={() => setActiveTab('export')}
          style={{
            ...styles.navButton,
            borderBottom: activeTab === 'export' ? '2px solid #c0392b' : 'none',
            color: activeTab === 'export' ? '#e9e5da' : '#636077',
          }}
        >
          📤 Export
        </button>
      </nav>

      <main style={styles.main}>
        {activeTab === 'verification' && <VerificationEngine />}
        {activeTab === 'press' && <PressAnalyzer />}
        {activeTab === 'viral' && <ViralScanner />}
        {activeTab === 'calendar' && <ContentCalendar />}
        {activeTab === 'export' && <ExportPanel />}
      </main>

      <footer style={styles.footer}>
        <p>✅ 5 components live: Verification Engine • Press Analyzer • Viral Scanner • Content Calendar • Export Panel</p>
      </footer>
    </div>
  );
}

const styles = {
  app: {
    minHeight: '100vh',
    backgroundColor: '#09090f',
    color: '#e9e5da',
    fontFamily: "'Lato', sans-serif",
  },
  header: {
    backgroundColor: '#0e0e18',
    borderBottom: '1px solid #1b1b2a',
    padding: '20px',
    textAlign: 'center',
  },
  title: {
    margin: 0,
    fontSize: 28,
    fontWeight: 700,
    fontFamily: "'Playfair Display', serif",
  },
  tagline: {
    margin: '8px 0 0 0',
    color: '#636077',
    fontSize: 14,
  },
  nav: {
    display: 'flex',
    borderBottom: '1px solid #1b1b2a',
    backgroundColor: '#0e0e18',
    padding: '0 20px',
  },
  navButton: {
    padding: '16px 20px',
    background: 'none',
    border: 'none',
    color: '#636077',
    fontSize: 14,
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'color 0.2s',
  },
  main: {
    minHeight: 'calc(100vh - 200px)',
  },
  footer: {
    backgroundColor: '#0e0e18',
    borderTop: '1px solid #1b1b2a',
    padding: '16px 20px',
    textAlign: 'center',
    color: '#636077',
    fontSize: 12,
  },
};
