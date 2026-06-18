import { useState } from 'react'

const STATUSES = ['Discovered', 'Prioritized', 'In Remediation', 'Done']
const SEVERITIES = ['Low', 'Medium', 'High', 'Critical']
const EFFORTS = ['1-3 days', '1-2 weeks', '2-4 weeks', '1+ months']

function GapsBoard({ project, gaps, onCreate, onUpdate, onDelete }) {
  const [showNewGapForm, setShowNewGapForm] = useState(false)
  const [newGap, setNewGap] = useState({
    pillar: 'Architecture Discipline',
    title: '',
    description: '',
    severity: 'Medium',
    effort: '1-3 days'
  })

  const gapsByStatus = STATUSES.reduce((acc, status) => {
    acc[status] = gaps.filter(g => g.status === status)
    return acc
  }, {})

  const handleCreateGap = async (e) => {
    e.preventDefault()
    await onCreate(newGap)
    setNewGap({
      pillar: 'Architecture Discipline',
      title: '',
      description: '',
      severity: 'Medium',
      effort: '1-3 days'
    })
    setShowNewGapForm(false)
  }

  const handleStatusChange = async (gapId, newStatus) => {
    const gap = gaps.find(g => g.id === gapId)
    await onUpdate(gapId, { ...gap, status: newStatus })
  }

  return (
    <div>
      {!showNewGapForm && (
        <button onClick={() => setShowNewGapForm(true)} style={{ marginBottom: '20px' }}>
          + New Gap/Bug
        </button>
      )}

      {showNewGapForm && (
        <div className="card" style={{ marginBottom: '30px' }}>
          <h3>New Gap or Bug</h3>
          <form onSubmit={handleCreateGap}>
            <select
              value={newGap.pillar}
              onChange={(e) => setNewGap({ ...newGap, pillar: e.target.value })}
              style={{ marginBottom: '10px', padding: '8px', border: '1px solid var(--border)' }}
            >
              <option>Architecture Discipline</option>
              <option>Build Quality In</option>
              <option>Verification & Validation</option>
              <option>CI & Safe Delivery</option>
              <option>Root-Cause Improvement</option>
              <option>Security & Privacy</option>
              <option>Observability</option>
              <option>Maintainability</option>
            </select>

            <input
              type="text"
              placeholder="Title"
              value={newGap.title}
              onChange={(e) => setNewGap({ ...newGap, title: e.target.value })}
              required
              style={{ marginBottom: '10px' }}
            />

            <textarea
              placeholder="Description"
              value={newGap.description}
              onChange={(e) => setNewGap({ ...newGap, description: e.target.value })}
              required
              style={{ marginBottom: '10px', minHeight: '80px' }}
            />

            <select
              value={newGap.severity}
              onChange={(e) => setNewGap({ ...newGap, severity: e.target.value })}
              style={{ marginBottom: '10px', marginRight: '10px', padding: '8px', border: '1px solid var(--border)', width: 'calc(50% - 5px)' }}
            >
              {SEVERITIES.map(s => <option key={s}>{s}</option>)}
            </select>

            <select
              value={newGap.effort}
              onChange={(e) => setNewGap({ ...newGap, effort: e.target.value })}
              style={{ marginBottom: '10px', padding: '8px', border: '1px solid var(--border)', width: 'calc(50% - 5px)' }}
            >
              {EFFORTS.map(e => <option key={e}>{e}</option>)}
            </select>

            <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
              <button type="submit">Create</button>
              <button type="button" onClick={() => setShowNewGapForm(false)} style={{ background: '#999' }}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="kanban">
        {STATUSES.map((status) => (
          <div key={status} className="kanban-col">
            <h4>{status} ({gapsByStatus[status].length})</h4>
            {gapsByStatus[status].map((gap) => (
              <div key={gap.id} className="kanban-card">
                <div className="kanban-card-title">{gap.title}</div>
                <div className="kanban-card-meta">
                  <div>{gap.pillar}</div>
                  <div>Severity: {gap.severity}</div>
                  <div>Effort: {gap.effort}</div>
                </div>
                <div style={{ marginTop: '8px', display: 'flex', gap: '5px', fontSize: '11px' }}>
                  {status !== 'Done' && (
                    <select
                      value={status}
                      onChange={(e) => handleStatusChange(gap.id, e.target.value)}
                      style={{ padding: '4px', border: '1px solid var(--border)', fontSize: '11px' }}
                    >
                      {STATUSES.map(s => <option key={s}>{s}</option>)}
                    </select>
                  )}
                  <button
                    onClick={() => onDelete(gap.id)}
                    style={{ background: '#ccc', color: '#333', padding: '4px 8px', flex: 1, fontSize: '11px' }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

export default GapsBoard
