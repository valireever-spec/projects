import React, { useState } from 'react';
import { detectRussiaFlag, classifySource, scoreVerification } from '../../utils/credibilityScorer';

export default function VerificationEngine() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const verify = async () => {
    if (!input.trim()) {
      setError('Enter a story claim or URL to verify');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const apiKey = process.env.REACT_APP_NEWSAPI;
      if (!apiKey) {
        throw new Error('NewsAPI key not configured');
      }

      const russiaFlag = detectRussiaFlag(input);

      // Search NewsAPI for articles about the claim
      const searchQuery = encodeURIComponent(input.substring(0, 100));
      const newsResponse = await fetch(
        `https://newsapi.org/v2/everything?q=${searchQuery}&sortBy=relevancy&language=en&pageSize=10&apiKey=${apiKey}`
      );

      if (!newsResponse.ok) {
        throw new Error(`NewsAPI error: ${newsResponse.status}`);
      }

      const newsData = await newsResponse.json();
      const articles = newsData.articles || [];

      // Convert articles to sources
      const sources = articles.slice(0, 8).map((article, idx) => ({
        name: article.source.name,
        url: article.url,
        type: 'news',
        description: article.description || article.title,
        relevance: 10 - idx,
        author: article.author,
        publishedAt: article.publishedAt,
      })).map(src => ({
        ...src,
        credibility: classifySource(src),
      }));

      const verification = scoreVerification(sources, russiaFlag);

      setResult({
        input,
        status: verification.status,
        requiresHold: verification.requiresHold,
        message: verification.message,
        russiaFlag,
        sources,
        analysis: sources.length > 0
          ? `Found ${sources.length} news articles about this topic. Top sources include ${sources
              .slice(0, 3)
              .map(s => s.name)
              .join(', ')}.`
          : 'No news articles found about this claim.',
        timestamp: new Date().toISOString(),
      });
    } catch (err) {
      setError(err.message || 'Verification failed. Check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      verified: '#27ae78',
      partial: '#f0a500',
      unverified: '#c0392b',
    };
    return colors[status] || '#636077';
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2>Verification Engine</h2>
        <p style={styles.subtitle}>Verify claims and find credible sources</p>
      </div>

      <div style={styles.infoBox}>
        <p style={styles.infoText}>
          🔍 Powered by NewsAPI — searches millions of news articles to verify claims and find sources
        </p>
        <p style={styles.infoText}>
          Finds credible sources, checks for Russia-related stories, and applies verification rules
        </p>
      </div>

      <textarea
        placeholder="Enter story claim, headline, or URL to verify..."
        value={input}
        onChange={e => setInput(e.target.value)}
        style={styles.textarea}
      />

      <button
        onClick={verify}
        disabled={loading}
        style={{
          ...styles.button,
          opacity: loading ? 0.6 : 1,
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? 'Verifying...' : 'Verify Story'}
      </button>

      {error && <div style={styles.error}>{error}</div>}

      {result && (
        <div style={styles.result}>
          <div style={styles.statusBar}>
            <div
              style={{
                ...styles.statusBadge,
                backgroundColor: getStatusColor(result.status),
              }}
            >
              {result.status.toUpperCase()}
            </div>
            {result.russiaFlag && (
              <div style={styles.russiaFlagBadge}>🚩 RUSSIA FLAG</div>
            )}
            {result.requiresHold && (
              <div style={styles.holdBadge}>⏸️ 24H HOLD</div>
            )}
          </div>

          <div style={styles.message}>{result.message}</div>

          <div style={styles.section}>
            <h3>Claim</h3>
            <p style={styles.quote}>{result.input}</p>
          </div>

          {result.analysis && (
            <div style={styles.section}>
              <h3>Analysis</h3>
              <p>{result.analysis}</p>
            </div>
          )}

          <div style={styles.section}>
            <h3>Sources Found ({result.sources.length})</h3>
            {result.sources.length === 0 ? (
              <p style={styles.muted}>No credible sources found</p>
            ) : (
              result.sources.map((src, idx) => (
                <div key={idx} style={styles.sourceCard}>
                  <div style={styles.sourceHeader}>
                    <span style={{ fontWeight: 600 }}>{src.name}</span>
                    <span
                      style={{
                        ...styles.credibilityBadge,
                        backgroundColor:
                          src.credibility.score >= 9
                            ? '#27ae78'
                            : src.credibility.score >= 7
                              ? '#f0a500'
                              : '#c0392b',
                      }}
                    >
                      {src.credibility.label}
                    </span>
                  </div>
                  <p style={styles.sourceDescription}>{src.description}</p>
                  {src.url && (
                    <a href={src.url} target="_blank" rel="noopener noreferrer" style={styles.link}>
                      {src.url}
                    </a>
                  )}
                </div>
              ))
            )}
          </div>

          <div style={styles.footer}>
            Verified at {new Date(result.timestamp).toLocaleString()}
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 700,
    margin: '0 auto',
    padding: 20,
    fontFamily: "'Lato', sans-serif",
    color: '#e9e5da',
    backgroundColor: '#09090f',
    minHeight: '100vh',
  },
  header: {
    marginBottom: 30,
  },
  subtitle: {
    color: '#636077',
    fontSize: 14,
    margin: '8px 0 0 0',
  },
  infoBox: {
    backgroundColor: 'rgba(39, 174, 120, 0.1)',
    border: '1px solid #27ae78',
    padding: 14,
    borderRadius: 6,
    marginBottom: 20,
  },
  infoText: {
    margin: '8px 0',
    fontSize: 13,
    color: '#b0a89a',
    lineHeight: 1.5,
  },
  apiKeyBanner: {
    backgroundColor: 'rgba(240, 165, 0, 0.1)',
    border: '1px solid #f0a500',
    padding: '12px 14px',
    borderRadius: 6,
    fontSize: 13,
    marginBottom: 20,
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  linkButton: {
    background: 'none',
    border: 'none',
    color: '#1a6bb5',
    cursor: 'pointer',
    textDecoration: 'underline',
    padding: 0,
    fontSize: 13,
    font: 'inherit',
  },
  apiKeyBox: {
    backgroundColor: '#0e0e18',
    border: '1px solid #1b1b2a',
    padding: 14,
    borderRadius: 6,
    marginBottom: 20,
    display: 'flex',
    gap: 10,
  },
  textarea: {
    width: '100%',
    minHeight: 100,
    padding: 12,
    backgroundColor: '#0e0e18',
    color: '#e9e5da',
    border: '1px solid #1b1b2a',
    borderRadius: 6,
    marginBottom: 12,
    fontFamily: "'Lato', sans-serif",
    fontSize: 14,
    resize: 'vertical',
  },
  input: {
    flex: 1,
    padding: '10px 12px',
    backgroundColor: '#09090f',
    color: '#e9e5da',
    border: '1px solid #1b1b2a',
    borderRadius: 4,
    fontSize: 13,
    fontFamily: 'inherit',
  },
  button: {
    width: '100%',
    padding: 12,
    backgroundColor: '#c0392b',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    fontSize: 14,
    fontWeight: 600,
    cursor: 'pointer',
    marginBottom: 12,
  },
  error: {
    backgroundColor: 'rgba(192, 57, 43, 0.1)',
    border: '1px solid #c0392b',
    color: '#ff6b6b',
    padding: 12,
    borderRadius: 6,
    fontSize: 13,
    marginBottom: 12,
  },
  result: {
    backgroundColor: '#0e0e18',
    border: '1px solid #1b1b2a',
    borderRadius: 8,
    padding: 16,
    marginTop: 20,
  },
  statusBar: {
    display: 'flex',
    gap: 8,
    marginBottom: 16,
    flexWrap: 'wrap',
  },
  statusBadge: {
    padding: '6px 12px',
    borderRadius: 4,
    fontSize: 12,
    fontWeight: 600,
    color: '#fff',
  },
  russiaFlagBadge: {
    backgroundColor: '#e74c3c',
    color: '#fff',
    padding: '6px 12px',
    borderRadius: 4,
    fontSize: 12,
    fontWeight: 600,
  },
  holdBadge: {
    backgroundColor: '#f0a500',
    color: '#000',
    padding: '6px 12px',
    borderRadius: 4,
    fontSize: 12,
    fontWeight: 600,
  },
  message: {
    backgroundColor: 'rgba(39, 174, 120, 0.1)',
    border: '1px solid #27ae78',
    padding: 12,
    borderRadius: 6,
    marginBottom: 16,
    fontSize: 13,
    color: '#a0d995',
  },
  section: {
    marginBottom: 16,
  },
  quote: {
    backgroundColor: '#09090f',
    padding: 12,
    borderLeft: '3px solid #c0392b',
    fontSize: 13,
    fontStyle: 'italic',
    color: '#b0a89a',
  },
  sourceCard: {
    backgroundColor: '#09090f',
    border: '1px solid #1b1b2a',
    padding: 12,
    borderRadius: 6,
    marginBottom: 10,
    fontSize: 13,
  },
  sourceHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: 10,
    marginBottom: 8,
  },
  credibilityBadge: {
    padding: '4px 8px',
    borderRadius: 3,
    fontSize: 11,
    fontWeight: 600,
    color: '#fff',
    whiteSpace: 'nowrap',
  },
  sourceDescription: {
    color: '#b0a89a',
    margin: '4px 0 8px 0',
  },
  link: {
    color: '#1a6bb5',
    textDecoration: 'none',
    fontSize: 12,
    wordBreak: 'break-all',
  },
  footer: {
    color: '#636077',
    fontSize: 12,
    textAlign: 'right',
    marginTop: 16,
    paddingTop: 12,
    borderTop: '1px solid #1b1b2a',
  },
  muted: {
    color: '#636077',
  },
};
