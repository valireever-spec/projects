import React, { useState } from 'react';
import { OUTLETS_BY_LANGUAGE } from '../../utils/outletConfig';

export default function ExportPanel() {
  const [script, setScript] = useState({
    headline: '',
    hook: '',
    whatHappened: '',
    whyItMatters: '',
    source: { name: '', url: '', date: '' },
    callToAction: 'Follow for more ignored signals',
    language: 'en',
    platform: 'youtube',
    sources: [],
  });

  const [exported, setExported] = useState(null);

  const updateScript = (field, value) => {
    setScript({ ...script, [field]: value });
  };

  const updateSource = (field, value) => {
    setScript({
      ...script,
      source: { ...script.source, [field]: value },
    });
  };

  const addSourceToList = () => {
    if (script.source.name.trim()) {
      setScript({
        ...script,
        sources: [...script.sources, { ...script.source }],
        source: { name: '', url: '', date: '' },
      });
    }
  };

  const removeSource = (idx) => {
    setScript({
      ...script,
      sources: script.sources.filter((_, i) => i !== idx),
    });
  };

  const generateProductionScript = () => {
    const duration = {
      hook: '3-5s',
      whatHappened: '15-20s',
      whyItMatters: '15-20s',
      source: '5s',
      cta: '5-7s',
    };

    const timeline = [
      { time: '0:00', section: 'HOOK', content: script.hook, duration: duration.hook },
      {
        time: '0:05',
        section: 'WHAT HAPPENED',
        content: script.whatHappened,
        duration: duration.whatHappened,
      },
      {
        time: '0:25',
        section: 'WHY IT MATTERS',
        content: script.whyItMatters,
        duration: duration.whyItMatters,
      },
      {
        time: '0:45',
        section: 'SOURCE',
        content: `${script.source.name}${script.source.date ? ` (${script.source.date})` : ''}`,
        duration: duration.source,
      },
      {
        time: '0:50',
        section: 'CALL TO ACTION',
        content: script.callToAction,
        duration: duration.cta,
      },
    ];

    const metadata = {
      headline: script.headline,
      language: OUTLETS_BY_LANGUAGE[script.language].name,
      platform: script.platform === 'youtube' ? 'YouTube Shorts' : 'TikTok',
      estimatedDuration: '50-60 seconds',
      sourcesCount: script.sources.length,
      generatedAt: new Date().toISOString(),
    };

    const sourcesList = script.sources
      .map(
        (s, i) =>
          `[${i + 1}] ${s.name}${s.url ? ` — ${s.url}` : ''}${s.date ? ` (${s.date})` : ''}`
      )
      .join('\n');

    setExported({
      timeline,
      metadata,
      sourcesList,
      fullScript: `HEADLINE: ${script.headline}\n\n${timeline.map(t => `${t.section} [${t.time} — ${t.duration}]\n${t.content}`).join('\n\n')}\n\nSOURCES:\n${sourcesList}`,
    });
  };

  const downloadJSON = () => {
    const data = {
      script,
      exported,
      timestamp: new Date().toISOString(),
    };
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${script.headline || 'script'}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadText = () => {
    const text = exported?.fullScript || script.headline;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${script.headline || 'script'}_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2>Export Panel</h2>
        <p style={styles.subtitle}>Format verified stories as production-ready scripts</p>
      </div>

      <div style={styles.editorSection}>
        <h3 style={styles.sectionTitle}>Story Details</h3>

        <div style={styles.fieldGroup}>
          <label style={styles.label}>Headline</label>
          <input
            type="text"
            placeholder="Story headline"
            value={script.headline}
            onChange={e => updateScript('headline', e.target.value)}
            style={styles.input}
          />
        </div>

        <div style={styles.twoColumn}>
          <div style={styles.fieldGroup}>
            <label style={styles.label}>Language</label>
            <select
              value={script.language}
              onChange={e => updateScript('language', e.target.value)}
              style={styles.select}
            >
              {Object.entries(OUTLETS_BY_LANGUAGE).map(([code, config]) => (
                <option key={code} value={code}>
                  {config.flag} {config.name}
                </option>
              ))}
            </select>
          </div>
          <div style={styles.fieldGroup}>
            <label style={styles.label}>Platform</label>
            <select
              value={script.platform}
              onChange={e => updateScript('platform', e.target.value)}
              style={styles.select}
            >
              <option value="youtube">YouTube Shorts</option>
              <option value="tiktok">TikTok</option>
            </select>
          </div>
        </div>

        <h3 style={styles.sectionTitle}>Narration Script</h3>

        <div style={styles.fieldGroup}>
          <label style={styles.label}>Hook (3-5s) — What wasn't reported?</label>
          <textarea
            placeholder="State the fact that wasn't reported..."
            value={script.hook}
            onChange={e => updateScript('hook', e.target.value)}
            style={styles.textarea}
          />
        </div>

        <div style={styles.fieldGroup}>
          <label style={styles.label}>What Happened (15-20s) — The verified facts</label>
          <textarea
            placeholder="Clearly state what happened..."
            value={script.whatHappened}
            onChange={e => updateScript('whatHappened', e.target.value)}
            style={styles.textarea}
          />
        </div>

        <div style={styles.fieldGroup}>
          <label style={styles.label}>Why It Matters (15-20s) — Impact for Europeans</label>
          <textarea
            placeholder="Explain the direct implication..."
            value={script.whyItMatters}
            onChange={e => updateScript('whyItMatters', e.target.value)}
            style={styles.textarea}
          />
        </div>

        <div style={styles.fieldGroup}>
          <label style={styles.label}>Call to Action (5-7s)</label>
          <input
            type="text"
            placeholder="E.g., 'Follow for more ignored signals'"
            value={script.callToAction}
            onChange={e => updateScript('callToAction', e.target.value)}
            style={styles.input}
          />
        </div>

        <h3 style={styles.sectionTitle}>Sources</h3>

        <div style={styles.sourceInput}>
          <div style={styles.sourceField}>
            <label style={styles.label}>Source Name</label>
            <input
              type="text"
              placeholder="e.g., EU Commission Official Statement"
              value={script.source.name}
              onChange={e => updateSource('name', e.target.value)}
              style={styles.input}
            />
          </div>

          <div style={styles.sourceField}>
            <label style={styles.label}>URL</label>
            <input
              type="text"
              placeholder="https://..."
              value={script.source.url}
              onChange={e => updateSource('url', e.target.value)}
              style={styles.input}
            />
          </div>

          <div style={styles.sourceField}>
            <label style={styles.label}>Date</label>
            <input
              type="text"
              placeholder="June 2024"
              value={script.source.date}
              onChange={e => updateSource('date', e.target.value)}
              style={styles.input}
            />
          </div>

          <button onClick={addSourceToList} style={styles.addSourceBtn}>
            Add Source
          </button>
        </div>

        {script.sources.length > 0 && (
          <div style={styles.sourcesList}>
            {script.sources.map((src, idx) => (
              <div key={idx} style={styles.sourceItem}>
                <div>
                  <div style={styles.sourceName}>{src.name}</div>
                  {src.url && <div style={styles.sourceUrl}>{src.url}</div>}
                  {src.date && <div style={styles.sourceDate}>{src.date}</div>}
                </div>
                <button
                  onClick={() => removeSource(idx)}
                  style={styles.removeSourceBtn}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        <button
          onClick={generateProductionScript}
          style={styles.generateBtn}
        >
          Generate Production Script
        </button>
      </div>

      {exported && (
        <div style={styles.previewSection}>
          <h3 style={styles.sectionTitle}>Production Script Preview</h3>

          <div style={styles.metadata}>
            <div style={styles.metaItem}>
              <span style={styles.metaLabel}>Headline:</span>
              <span>{exported.metadata.headline}</span>
            </div>
            <div style={styles.metaItem}>
              <span style={styles.metaLabel}>Language:</span>
              <span>{exported.metadata.language}</span>
            </div>
            <div style={styles.metaItem}>
              <span style={styles.metaLabel}>Platform:</span>
              <span>{exported.metadata.platform}</span>
            </div>
            <div style={styles.metaItem}>
              <span style={styles.metaLabel}>Duration:</span>
              <span>{exported.metadata.estimatedDuration}</span>
            </div>
            <div style={styles.metaItem}>
              <span style={styles.metaLabel}>Sources:</span>
              <span>{exported.metadata.sourcesCount}</span>
            </div>
          </div>

          <div style={styles.timeline}>
            {exported.timeline.map((segment, idx) => (
              <div key={idx} style={styles.timelineSegment}>
                <div style={styles.timelineTime}>{segment.time}</div>
                <div style={styles.timelineContent}>
                  <div style={styles.timelineSection}>{segment.section}</div>
                  <div style={styles.timelineText}>{segment.content}</div>
                  <div style={styles.timelineDuration}>{segment.duration}</div>
                </div>
              </div>
            ))}
          </div>

          <div style={styles.sourcesBox}>
            <h4 style={styles.sourcesTitle}>Sources (shown on-screen)</h4>
            <pre style={styles.sourcesPre}>{exported.sourcesList}</pre>
          </div>

          <div style={styles.downloadSection}>
            <button onClick={downloadJSON} style={styles.downloadBtn}>
              📥 Download JSON
            </button>
            <button onClick={downloadText} style={styles.downloadBtn}>
              📄 Download Text
            </button>
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
  editorSection: {
    backgroundColor: '#0e0e18',
    border: '1px solid #1b1b2a',
    padding: 20,
    borderRadius: 8,
    marginBottom: 20,
  },
  sectionTitle: {
    margin: '0 0 16px 0',
    fontSize: 14,
    fontWeight: 600,
    color: '#e9e5da',
  },
  fieldGroup: {
    marginBottom: 16,
  },
  label: {
    display: 'block',
    fontSize: 12,
    fontWeight: 600,
    color: '#636077',
    marginBottom: 6,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  input: {
    width: '100%',
    padding: '10px 12px',
    backgroundColor: '#09090f',
    color: '#e9e5da',
    border: '1px solid #1b1b2a',
    borderRadius: 4,
    fontSize: 13,
    fontFamily: 'inherit',
    boxSizing: 'border-box',
  },
  select: {
    width: '100%',
    padding: '10px 12px',
    backgroundColor: '#09090f',
    color: '#e9e5da',
    border: '1px solid #1b1b2a',
    borderRadius: 4,
    fontSize: 13,
    fontFamily: 'inherit',
    cursor: 'pointer',
    boxSizing: 'border-box',
  },
  textarea: {
    width: '100%',
    minHeight: 80,
    padding: '10px 12px',
    backgroundColor: '#09090f',
    color: '#e9e5da',
    border: '1px solid #1b1b2a',
    borderRadius: 4,
    fontSize: 13,
    fontFamily: "'Fira Code', monospace",
    resize: 'vertical',
    boxSizing: 'border-box',
  },
  twoColumn: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 16,
    marginBottom: 16,
  },
  sourceInput: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: 10,
    marginBottom: 16,
    alignItems: 'flex-end',
  },
  sourceField: {
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
  },
  addSourceBtn: {
    padding: '10px 16px',
    backgroundColor: '#27ae78',
    color: '#fff',
    border: 'none',
    borderRadius: 4,
    fontSize: 12,
    fontWeight: 600,
    cursor: 'pointer',
  },
  sourcesList: {
    display: 'grid',
    gap: 8,
    marginBottom: 16,
  },
  sourceItem: {
    backgroundColor: '#09090f',
    border: '1px solid #1b1b2a',
    padding: 10,
    borderRadius: 4,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sourceName: {
    fontSize: 12,
    fontWeight: 600,
  },
  sourceUrl: {
    fontSize: 11,
    color: '#1a6bb5',
    marginTop: 4,
  },
  sourceDate: {
    fontSize: 11,
    color: '#636077',
    marginTop: 2,
  },
  removeSourceBtn: {
    background: 'none',
    border: 'none',
    color: '#636077',
    cursor: 'pointer',
    fontSize: 14,
    padding: 0,
  },
  generateBtn: {
    width: '100%',
    padding: 12,
    backgroundColor: '#c0392b',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    fontSize: 14,
    fontWeight: 600,
    cursor: 'pointer',
  },
  previewSection: {
    backgroundColor: '#0e0e18',
    border: '1px solid #1b1b2a',
    padding: 20,
    borderRadius: 8,
  },
  metadata: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: 12,
    marginBottom: 20,
    padding: 12,
    backgroundColor: '#09090f',
    borderRadius: 4,
  },
  metaItem: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: 12,
    gap: 10,
  },
  metaLabel: {
    fontWeight: 600,
    color: '#636077',
  },
  timeline: {
    marginBottom: 20,
  },
  timelineSegment: {
    display: 'grid',
    gridTemplateColumns: '60px 1fr',
    gap: 12,
    marginBottom: 12,
    padding: 12,
    backgroundColor: '#09090f',
    borderLeft: '3px solid #c0392b',
    borderRadius: 4,
  },
  timelineTime: {
    fontSize: 12,
    fontWeight: 700,
    color: '#c0392b',
  },
  timelineContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: 4,
  },
  timelineSection: {
    fontSize: 11,
    fontWeight: 600,
    color: '#636077',
    textTransform: 'uppercase',
  },
  timelineText: {
    fontSize: 13,
    color: '#e9e5da',
    lineHeight: 1.4,
  },
  timelineDuration: {
    fontSize: 11,
    color: '#636077',
    marginTop: 4,
  },
  sourcesBox: {
    backgroundColor: '#09090f',
    border: '1px solid #1b1b2a',
    padding: 12,
    borderRadius: 4,
    marginBottom: 20,
  },
  sourcesTitle: {
    margin: '0 0 10px 0',
    fontSize: 12,
    fontWeight: 600,
    color: '#e9e5da',
  },
  sourcesPre: {
    margin: 0,
    fontSize: 11,
    color: '#b0a89a',
    fontFamily: "'Fira Code', monospace",
    overflow: 'auto',
  },
  downloadSection: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 12,
  },
  downloadBtn: {
    padding: 12,
    backgroundColor: '#1a6bb5',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    fontSize: 13,
    fontWeight: 600,
    cursor: 'pointer',
  },
};
