import React, { useState } from 'react';
import { OUTLETS_BY_LANGUAGE } from '../../utils/outletConfig';

export default function ContentCalendar() {
  const languages = Object.keys(OUTLETS_BY_LANGUAGE);
  const platforms = ['youtube', 'tiktok'];
  const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  const [calendar, setCalendar] = useState({});
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [storyInput, setStoryInput] = useState('');
  const [stories, setStories] = useState([]);

  const addStory = () => {
    if (storyInput.trim()) {
      setStories([
        ...stories,
        {
          id: Date.now(),
          title: storyInput,
          status: 'draft',
          language: 'en',
          platform: 'youtube',
        },
      ]);
      setStoryInput('');
    }
  };

  const getSlotKey = (lang, platform, day) => `${lang}-${platform}-${day}`;

  const scheduleStory = (storyId, lang, platform, day) => {
    const slot = getSlotKey(lang, platform, day);
    const story = stories.find(s => s.id === storyId);
    if (story) {
      setCalendar({
        ...calendar,
        [slot]: { ...story, scheduledDay: day },
      });
      setSelectedSlot(null);
    }
  };

  const removeFromSlot = (lang, platform, day) => {
    const slot = getSlotKey(lang, platform, day);
    const newCalendar = { ...calendar };
    delete newCalendar[slot];
    setCalendar(newCalendar);
  };

  const getStatusColor = (status) => {
    const colors = {
      draft: '#636077',
      verified: '#27ae78',
      scripted: '#1a6bb5',
      ready: '#f0a500',
      published: '#a0d995',
    };
    return colors[status] || '#636077';
  };

  const plannedCount = Object.keys(calendar).length;
  const unscheduledCount = stories.length - plannedCount;

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2>Content Calendar</h2>
        <p style={styles.subtitle}>Plan content across 5 languages × 2 platforms × 7 days</p>
      </div>

      <div style={styles.statsBar}>
        <div style={styles.stat}>
          <span style={styles.statNumber}>{plannedCount}</span>
          <span style={styles.statLabel}>Scheduled</span>
        </div>
        <div style={styles.stat}>
          <span style={styles.statNumber}>{unscheduledCount}</span>
          <span style={styles.statLabel}>Waiting</span>
        </div>
        <div style={styles.stat}>
          <span style={styles.statNumber}>{stories.length}</span>
          <span style={styles.statLabel}>Total Stories</span>
        </div>
      </div>

      <div style={styles.storyInputSection}>
        <h3 style={styles.sectionTitle}>Add Story</h3>
        <div style={styles.inputGroup}>
          <input
            type="text"
            placeholder="Story title or description..."
            value={storyInput}
            onChange={e => setStoryInput(e.target.value)}
            onKeyPress={e => e.key === 'Enter' && addStory()}
            style={styles.input}
          />
          <button onClick={addStory} style={styles.button}>
            Add
          </button>
        </div>
      </div>

      {stories.length > 0 && (
        <div style={styles.storyPoolSection}>
          <h3 style={styles.sectionTitle}>Unscheduled Stories ({unscheduledCount})</h3>
          <div style={styles.storyPool}>
            {stories
              .filter(
                s =>
                  !Object.values(calendar).some(
                    scheduled => scheduled.id === s.id
                  )
              )
              .map(story => (
                <div key={story.id} style={styles.storyPoolItem}>
                  <div>
                    <div style={styles.poolStoryTitle}>{story.title}</div>
                    <div style={styles.poolStoryMeta}>
                      <span style={{ ...styles.badge, backgroundColor: '#636077' }}>
                        {story.status}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedSlot(story.id)}
                    style={styles.scheduleBtn}
                  >
                    Schedule →
                  </button>
                </div>
              ))}
          </div>
        </div>
      )}

      {selectedSlot && (
        <div style={styles.modal}>
          <div style={styles.modalContent}>
            <div style={styles.modalHeader}>
              <h4>Select Slot for "{stories.find(s => s.id === selectedSlot)?.title}"</h4>
              <button
                onClick={() => setSelectedSlot(null)}
                style={styles.closeBtn}
              >
                ✕
              </button>
            </div>
            <div style={styles.slotGrid}>
              {languages.map(lang =>
                platforms.map(platform =>
                  daysOfWeek.map(day => (
                    <button
                      key={`${lang}-${platform}-${day}`}
                      onClick={() =>
                        scheduleStory(selectedSlot, lang, platform, daysOfWeek.indexOf(day))
                      }
                      style={styles.slotOption}
                    >
                      <div style={styles.slotLabel}>
                        {OUTLETS_BY_LANGUAGE[lang].flag}
                      </div>
                      <div style={styles.slotDay}>{day}</div>
                      <div style={styles.slotPlat}>
                        {platform === 'youtube' ? '▶️' : '♪'}
                      </div>
                    </button>
                  ))
                )
              )}
            </div>
          </div>
        </div>
      )}

      <div style={styles.calendarSection}>
        <h3 style={styles.sectionTitle}>7-Day Schedule</h3>
        <div style={styles.calendarGrid}>
          {languages.map(lang =>
            platforms.map(platform => (
              <div key={`${lang}-${platform}`} style={styles.platformSection}>
                <div style={styles.platformHeader}>
                  <span>{OUTLETS_BY_LANGUAGE[lang].flag}</span>
                  <span>{platform === 'youtube' ? 'YouTube Shorts' : 'TikTok'}</span>
                </div>
                <div style={styles.daysRow}>
                  {daysOfWeek.map((day, idx) => {
                    const slotKey = getSlotKey(lang, platform, idx);
                    const scheduled = calendar[slotKey];
                    return (
                      <div
                        key={day}
                        style={{
                          ...styles.daySlot,
                          backgroundColor: scheduled ? '#0e0e18' : '#09090f',
                          borderColor: scheduled ? '#1a6bb5' : '#1b1b2a',
                        }}
                      >
                        <div style={styles.dayLabel}>{day}</div>
                        {scheduled ? (
                          <div style={styles.scheduledStory}>
                            <div
                              style={{
                                ...styles.storyStatus,
                                backgroundColor: getStatusColor(scheduled.status),
                              }}
                            >
                              {scheduled.status}
                            </div>
                            <div style={styles.storyTitleSmall}>
                              {scheduled.title}
                            </div>
                            <button
                              onClick={() => removeFromSlot(lang, platform, idx)}
                              style={styles.removeBtn}
                            >
                              ✕
                            </button>
                          </div>
                        ) : (
                          <div style={styles.emptySlot}>
                            <button
                              onClick={() => setSelectedSlot(null)}
                              style={styles.addSlotBtn}
                            >
                              +
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div style={styles.legend}>
        <div style={styles.legendItem}>
          <div style={{ ...styles.legendColor, backgroundColor: '#636077' }} />
          <span>Draft</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{ ...styles.legendColor, backgroundColor: '#27ae78' }} />
          <span>Verified</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{ ...styles.legendColor, backgroundColor: '#1a6bb5' }} />
          <span>Scripted</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{ ...styles.legendColor, backgroundColor: '#f0a500' }} />
          <span>Ready</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{ ...styles.legendColor, backgroundColor: '#a0d995' }} />
          <span>Published</span>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 1200,
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
  statsBar: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: 12,
    marginBottom: 20,
  },
  stat: {
    backgroundColor: '#0e0e18',
    border: '1px solid #1b1b2a',
    padding: 12,
    borderRadius: 6,
    textAlign: 'center',
  },
  statNumber: {
    display: 'block',
    fontSize: 24,
    fontWeight: 700,
    color: '#c0392b',
  },
  statLabel: {
    display: 'block',
    fontSize: 11,
    color: '#636077',
    marginTop: 4,
    textTransform: 'uppercase',
  },
  sectionTitle: {
    margin: '0 0 12px 0',
    fontSize: 14,
    fontWeight: 600,
    color: '#e9e5da',
  },
  storyInputSection: {
    backgroundColor: '#0e0e18',
    border: '1px solid #1b1b2a',
    padding: 16,
    borderRadius: 6,
    marginBottom: 20,
  },
  inputGroup: {
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
  button: {
    padding: '10px 20px',
    backgroundColor: '#c0392b',
    color: '#fff',
    border: 'none',
    borderRadius: 4,
    fontSize: 13,
    fontWeight: 600,
    cursor: 'pointer',
  },
  storyPoolSection: {
    backgroundColor: '#0e0e18',
    border: '1px solid #1b1b2a',
    padding: 16,
    borderRadius: 6,
    marginBottom: 20,
  },
  storyPool: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
    gap: 10,
  },
  storyPoolItem: {
    backgroundColor: '#09090f',
    border: '1px solid #1b1b2a',
    padding: 12,
    borderRadius: 4,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: 10,
  },
  poolStoryTitle: {
    fontSize: 12,
    fontWeight: 600,
    marginBottom: 6,
  },
  poolStoryMeta: {
    display: 'flex',
    gap: 6,
  },
  badge: {
    padding: '2px 6px',
    borderRadius: 2,
    fontSize: 10,
    fontWeight: 600,
    color: '#fff',
  },
  scheduleBtn: {
    padding: '6px 10px',
    backgroundColor: '#1a6bb5',
    color: '#fff',
    border: 'none',
    borderRadius: 3,
    fontSize: 11,
    fontWeight: 600,
    cursor: 'pointer',
    whiteSpace: 'nowrap',
  },
  modal: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  modalContent: {
    backgroundColor: '#0e0e18',
    border: '1px solid #1b1b2a',
    borderRadius: 8,
    padding: 20,
    maxWidth: 600,
    maxHeight: '80vh',
    overflow: 'auto',
  },
  modalHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
    paddingBottom: 12,
    borderBottom: '1px solid #1b1b2a',
  },
  closeBtn: {
    background: 'none',
    border: 'none',
    color: '#636077',
    fontSize: 20,
    cursor: 'pointer',
    padding: 0,
  },
  slotGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(60px, 1fr))',
    gap: 8,
  },
  slotOption: {
    padding: 10,
    backgroundColor: '#09090f',
    border: '1px solid #1b1b2a',
    borderRadius: 4,
    color: '#e9e5da',
    cursor: 'pointer',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 4,
    fontSize: 12,
    fontWeight: 500,
  },
  slotLabel: {
    fontSize: 14,
  },
  slotDay: {
    fontSize: 11,
    color: '#636077',
  },
  slotPlat: {
    fontSize: 10,
  },
  calendarSection: {
    marginBottom: 20,
  },
  calendarGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
    gap: 16,
  },
  platformSection: {
    backgroundColor: '#0e0e18',
    border: '1px solid #1b1b2a',
    borderRadius: 6,
    overflow: 'hidden',
  },
  platformHeader: {
    backgroundColor: '#09090f',
    padding: 10,
    fontWeight: 600,
    fontSize: 12,
    display: 'flex',
    justifyContent: 'space-between',
    borderBottom: '1px solid #1b1b2a',
  },
  daysRow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(7, 1fr)',
    gap: 0,
  },
  daySlot: {
    borderRight: '1px solid #1b1b2a',
    borderBottom: '1px solid #1b1b2a',
    padding: 8,
    minHeight: 120,
    position: 'relative',
    display: 'flex',
    flexDirection: 'column',
  },
  dayLabel: {
    fontSize: 10,
    fontWeight: 600,
    color: '#636077',
    marginBottom: 6,
    textTransform: 'uppercase',
  },
  emptySlot: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  addSlotBtn: {
    width: 32,
    height: 32,
    borderRadius: '50%',
    border: '2px dashed #1b1b2a',
    background: 'none',
    color: '#636077',
    fontSize: 18,
    cursor: 'pointer',
  },
  scheduledStory: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
    position: 'relative',
  },
  storyStatus: {
    padding: '2px 6px',
    borderRadius: 2,
    fontSize: 9,
    fontWeight: 600,
    color: '#fff',
    alignSelf: 'flex-start',
  },
  storyTitleSmall: {
    fontSize: 10,
    lineHeight: 1.3,
    color: '#b0a89a',
  },
  removeBtn: {
    position: 'absolute',
    top: 0,
    right: 0,
    background: 'none',
    border: 'none',
    color: '#636077',
    cursor: 'pointer',
    fontSize: 12,
    padding: 0,
  },
  legend: {
    display: 'flex',
    gap: 16,
    flexWrap: 'wrap',
    padding: 12,
    backgroundColor: '#0e0e18',
    borderRadius: 6,
    fontSize: 12,
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
  },
  legendColor: {
    width: 12,
    height: 12,
    borderRadius: 2,
  },
};
