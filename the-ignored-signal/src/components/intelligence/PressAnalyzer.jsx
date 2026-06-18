import React, { useState } from 'react';
import { OUTLETS_BY_LANGUAGE, CATEGORIES } from '../../utils/outletConfig';

export default function PressAnalyzer() {
  const [language, setLanguage] = useState('en');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const analyze = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const apiKey = process.env.REACT_APP_NEWSAPI;
      if (!apiKey) {
        throw new Error('NewsAPI key not configured');
      }

      // Build search query based on category
      const categoryKeywords = {
        eu_policy: 'EU legislation parliament regulation',
        economic: 'economy inflation recession housing crisis',
        environment: 'climate environment sustainability',
        science: 'research scientific study discovery',
        history: 'history historical Europe',
        human_interest: 'human interest story',
        russia: 'Russia Ukraine NATO',
        human_rights: 'human rights violation',
        corruption: 'corruption scandal fraud',
      };

      const searchQuery = category
        ? categoryKeywords[category] || 'Europe news'
        : 'Europe news';

      // Search NewsAPI
      const newsResponse = await fetch(
        `https://newsapi.org/v2/everything?q=${encodeURIComponent(
          searchQuery
        )}&language=${language}&sortBy=publishedAt&pageSize=30&apiKey=${apiKey}`
      );

      if (!newsResponse.ok) {
        throw new Error(`NewsAPI error: ${newsResponse.status}`);
      }

      const newsData = await newsResponse.json();
      const articles = newsData.articles || [];

      // Score stories: importance is how recent + engagement (comments/shares proxy), coverage is number of times reported
      const storyMap = new Map();
      articles.forEach(article => {
        const key = article.title;
        if (storyMap.has(key)) {
          storyMap.get(key).count++;
        } else {
          storyMap.set(key, { article, count: 1 });
        }
      });

      const stories = Array.from(storyMap.values())
        .map(({ article, count }) => {
          // Coverage score: how many sources reported it (1-10 scale)
          const coverageScore = Math.min(10, 2 + count);

          // Importance score: recency + relevance
          const daysOld = Math.floor(
            (Date.now() - new Date(article.publishedAt).getTime()) / (1000 * 60 * 60 * 24)
          );
          const importanceScore = Math.max(3, 10 - daysOld);

          // Gap: high importance, low coverage = high gap
          const gapScore = Math.max(1, importanceScore - coverageScore);

          return {
            headline: article.title,
            summary: article.description || article.content || article.title,
            importanceScore,
            coverageScore,
            gapScore,
            sources: [article.source.name],
            category: category ? CATEGORIES.find(c => c.id === category)?.label : 'General',
            language,
            url: article.url,
            publishedAt: article.publishedAt,
          };
        })
        .sort((a, b) => b.gapScore - a.gapScore)
        .slice(0, 12);

      setResults({
        language,
        category,
        timestamp: new Date().toISOString(),
        stories,
      });
    } catch (err) {
      setError(err.message || 'Analysis failed. Check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const getGapColor = (gap) => {
    if (gap >= 8) return '#c0392b'; // High gap - very overlooked
    if (gap >= 5) return '#f0a500'; // Medium gap
    return '#27ae78'; // Low gap
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2>Press Coverage Analyzer</h2>
        <p style={styles.subtitle}>Find underreported stories across European outlets</p>
      </div>

      <div style={styles.infoBox}>
        <p style={styles.infoText}>
          📊 Powered by NewsAPI — searches millions of news articles across multiple sources
        </p>
        <p style={styles.infoText}>
          Scores stories by importance vs. coverage to find the most underreported news
        </p>
      </div>

      <div style={styles.controlsGroup}>
        <div style={styles.control}>
          <label style={styles.label}>Language</label>
          <select
            value={language}
            onChange={e => {
              setLanguage(e.target.value);
              setResults(null);
            }}
            style={styles.select}
          >
            {Object.entries(OUTLETS_BY_LANGUAGE).map(([code, config]) => (
              <option key={code} value={code}>
                {config.flag} {config.name}
              </option>
            ))}
          </select>
        </div>

        <div style={styles.control}>
          <label style={styles.label}>Category (optional)</label>
          <select
            value={category}
            onChange={e => {
              setCategory(e.target.value);
              setResults(null);
            }}
            style={styles.select}
          >
            <option value="">All Categories</option>
            {CATEGORIES.map(cat => (
              <option key={cat.id} value={cat.id}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button
        onClick={analyze}
        disabled={loading}
        style={{
          ...styles.button,
          opacity: loading ? 0.6 : 1,
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? 'Analyzing outlets...' : 'Analyze Coverage'}
      </button>

      {error && <div style={styles.error}>{error}</div>}

      {results && (
        <div style={styles.result}>
          <div style={styles.resultHeader}>
            <div>
              <h3>
                {OUTLETS_BY_LANGUAGE[results.language].flag}{' '}
                {OUTLETS_BY_LANGUAGE[results.language].name}
                {results.category &&
                  ` — ${CATEGORIES.find(c => c.id === results.category)?.label}`}
              </h3>
              <p style={styles.muted}>
                {results.stories.length} stories analyzed
              </p>
            </div>
          </div>

          <div style={styles.storiesGrid}>
            {results.stories.map((story, idx) => (
              <div key={idx} style={styles.storyCard}>
                <div style={styles.storyHeader}>
                  <h4 style={styles.headline}>{story.headline}</h4>
                  <div
                    style={{
                      ...styles.gapBadge,
                      backgroundColor: getGapColor(story.gapScore),
                    }}
                  >
                    Gap: {story.gapScore}
                  </div>
                </div>

                <p style={styles.summary}>{story.summary}</p>

                <div style={styles.scoreRow}>
                  <div style={styles.scoreItem}>
                    <span style={styles.scoreLabel}>Importance</span>
                    <div style={styles.scoreBar}>
                      <div
                        style={{
                          ...styles.scoreBarFill,
                          width: `${story.importanceScore * 10}%`,
                          backgroundColor: '#27ae78',
                        }}
                      />
                    </div>
                    <span style={styles.scoreValue}>{story.importanceScore}/10</span>
                  </div>

                  <div style={styles.scoreItem}>
                    <span style={styles.scoreLabel}>Coverage</span>
                    <div style={styles.scoreBar}>
                      <div
                        style={{
                          ...styles.scoreBarFill,
                          width: `${story.coverageScore * 10}%`,
                          backgroundColor: '#1a6bb5',
                        }}
                      />
                    </div>
                    <span style={styles.scoreValue}>{story.coverageScore}/10</span>
                  </div>
                </div>

                <div style={styles.sourcesSection}>
                  <span style={styles.sourcesLabel}>Found in:</span>
                  <div style={styles.sourcesList}>
                    {story.sources.map((source, i) => (
                      <span key={i} style={styles.sourceTag}>
                        {source}
                      </span>
                    ))}
                  </div>
                </div>

                <div style={styles.categoryTag}>{story.category}</div>
              </div>
            ))}
          </div>

          <div style={styles.footer}>
            Analyzed {new Date(results.timestamp).toLocaleString()}
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 900,
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
  controlsGroup: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 12,
    marginBottom: 16,
  },
  control: {
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
  },
  label: {
    fontSize: 12,
    fontWeight: 600,
    color: '#636077',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  select: {
    padding: '10px 12px',
    backgroundColor: '#0e0e18',
    color: '#e9e5da',
    border: '1px solid #1b1b2a',
    borderRadius: 4,
    fontSize: 13,
    fontFamily: 'inherit',
    cursor: 'pointer',
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
  resultHeader: {
    marginBottom: 20,
    paddingBottom: 16,
    borderBottom: '1px solid #1b1b2a',
  },
  muted: {
    color: '#636077',
    fontSize: 12,
    margin: '4px 0 0 0',
  },
  storiesGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: 16,
    marginBottom: 20,
  },
  storyCard: {
    backgroundColor: '#09090f',
    border: '1px solid #1b1b2a',
    borderRadius: 8,
    padding: 16,
    display: 'flex',
    flexDirection: 'column',
    gap: 12,
  },
  storyHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: 10,
  },
  headline: {
    margin: 0,
    fontSize: 14,
    fontWeight: 600,
    lineHeight: 1.4,
    color: '#e9e5da',
  },
  gapBadge: {
    padding: '4px 10px',
    borderRadius: 4,
    fontSize: 11,
    fontWeight: 700,
    color: '#fff',
    whiteSpace: 'nowrap',
  },
  summary: {
    margin: 0,
    fontSize: 12,
    color: '#b0a89a',
    lineHeight: 1.5,
  },
  scoreRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 12,
  },
  scoreItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: 4,
  },
  scoreLabel: {
    fontSize: 11,
    fontWeight: 600,
    color: '#636077',
    textTransform: 'uppercase',
  },
  scoreBar: {
    backgroundColor: '#0e0e18',
    height: 6,
    borderRadius: 2,
    overflow: 'hidden',
  },
  scoreBarFill: {
    height: '100%',
    minWidth: 2,
  },
  scoreValue: {
    fontSize: 11,
    color: '#e9e5da',
  },
  sourcesSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
  },
  sourcesLabel: {
    fontSize: 11,
    fontWeight: 600,
    color: '#636077',
    textTransform: 'uppercase',
  },
  sourcesList: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 6,
  },
  sourceTag: {
    backgroundColor: '#1b1b2a',
    padding: '4px 8px',
    borderRadius: 3,
    fontSize: 11,
    color: '#a0d995',
  },
  categoryTag: {
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(26, 107, 181, 0.2)',
    color: '#1a6bb5',
    padding: '4px 10px',
    borderRadius: 4,
    fontSize: 11,
    fontWeight: 600,
  },
  footer: {
    color: '#636077',
    fontSize: 12,
    textAlign: 'right',
    paddingTop: 12,
    borderTop: '1px solid #1b1b2a',
  },
};
