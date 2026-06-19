import { useState, useEffect } from 'react'
import { suggestRequirementsForGap, linkRequirementToGap } from '../api'

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
  const [selectedGapForLinking, setSelectedGapForLinking] = useState(null)
  const [suggestedRequirements, setSuggestedRequirements] = useState([])
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  const [selectedRequirement, setSelectedRequirement] = useState(null)

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

  const handleLinkGap = async (gap) => {
    setSelectedGapForLinking(gap)
    setLoadingSuggestions(true)
    try {
      const { data } = await suggestRequirementsForGap(project.id, gap.id)
      setSuggestedRequirements(data)
    } catch (err) {
      console.error('Failed to get suggestions:', err)
      setSuggestedRequirements([])
    } finally {
      setLoadingSuggestions(false)
    }
  }

  const handleConfirmLink = async () => {
    if (!selectedRequirement || !selectedGapForLinking) {
      alert('Please select a requirement')
      return
    }

    try {
      await linkRequirementToGap(project.id, selectedGapForLinking.id, {
        requirement_id: selectedRequirement.id,
        acceptance_criterion_id: null
      })

      // Update gap with requirement info
      await onUpdate(selectedGapForLinking.id, {
        ...selectedGapForLinking,
        requirement_id: selectedRequirement.id
      })

      setSelectedGapForLinking(null)
      setSuggestedRequirements([])
      setSelectedRequirement(null)
      alert('Gap linked to requirement successfully!')
    } catch (err) {
      console.error('Failed to link requirement:', err)
      alert('Failed to link requirement')
    }
  }

  const handleCancelLink = () => {
    setSelectedGapForLinking(null)
    setSuggestedRequirements([])
    setSelectedRequirement(null)
  }

  return (
    <div>
      {selectedGapForLinking && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: '#fff',
            borderRadius: '8px',
            padding: '30px',
            maxWidth: '600px',
            width: '90%',
            maxHeight: '80vh',
            overflow: 'auto',
            boxShadow: '0 4px 20px rgba(0,0,0,0.2)'
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#0066cc' }}>
              Link Requirement to Gap: {selectedGapForLinking.title}
            </h3>
            <p style={{ color: '#999', fontSize: '12px', margin: '0 0 20px 0' }}>
              Select a requirement that this gap violates
            </p>

            {loadingSuggestions && <p style={{ color: '#999' }}>Loading suggestions...</p>}

            {!loadingSuggestions && suggestedRequirements.length === 0 && (
              <p style={{ color: '#999' }}>No matching requirements found</p>
            )}

            {!loadingSuggestions && suggestedRequirements.length > 0 && (
              <div style={{ marginBottom: '20px' }}>
                {suggestedRequirements.map(req => (
                  <div
                    key={req.id}
                    onClick={() => setSelectedRequirement(req)}
                    style={{
                      border: selectedRequirement?.id === req.id ? '2px solid #0066cc' : '1px solid #ddd',
                      borderRadius: '4px',
                      padding: '12px',
                      marginBottom: '10px',
                      cursor: 'pointer',
                      background: selectedRequirement?.id === req.id ? '#f0f8ff' : '#f9f9f9'
                    }}
                  >
                    <div style={{ fontWeight: 'bold', color: '#0066cc', marginBottom: '5px' }}>
                      {req.req_id}: {req.title}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>
                      Type: {req.req_type} | Category: {req.category}
                    </div>
                    <div style={{ fontSize: '11px', color: '#999' }}>
                      Match Score: {req.score}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
              <button
                onClick={handleCancelLink}
                style={{
                  background: '#999',
                  color: '#fff',
                  border: 'none',
                  padding: '10px 15px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmLink}
                disabled={!selectedRequirement}
                style={{
                  background: selectedRequirement ? '#4CAF50' : '#ccc',
                  color: '#fff',
                  border: 'none',
                  padding: '10px 15px',
                  borderRadius: '4px',
                  cursor: selectedRequirement ? 'pointer' : 'not-allowed',
                  fontWeight: 'bold'
                }}
              >
                Link to Requirement
              </button>
            </div>
          </div>
        </div>
      )}

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
                {gap.requirement_id && (
                  <div style={{ marginTop: '8px', padding: '6px', background: '#e8f5e9', borderRadius: '3px', fontSize: '11px', color: '#2e7d32', fontWeight: 'bold' }}>
                    ✓ Linked to requirement
                  </div>
                )}
                <div style={{ marginTop: '8px', display: 'flex', gap: '5px', fontSize: '11px', flexWrap: 'wrap' }}>
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
                    onClick={() => handleLinkGap(gap)}
                    style={{ background: '#2196F3', color: '#fff', padding: '4px 8px', fontSize: '11px', border: 'none', borderRadius: '3px', cursor: 'pointer' }}
                  >
                    {gap.requirement_id ? 'Edit Link' : 'Link Req'}
                  </button>
                  <button
                    onClick={() => onDelete(gap.id)}
                    style={{ background: '#ccc', color: '#333', padding: '4px 8px', fontSize: '11px', border: 'none', borderRadius: '3px', cursor: 'pointer' }}
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
