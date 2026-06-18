import { useState } from 'react'

const PILLARS = [
  { name: 'Architecture Discipline & Traceability', shortName: 'Architecture Discipline' },
  { name: 'Build Quality In / Error-Proofing', shortName: 'Build Quality In' },
  { name: 'Verification & Validation', shortName: 'Verification & Validation' },
  { name: 'Continuous Integration & Safe Delivery', shortName: 'CI & Safe Delivery' },
  { name: 'Root-Cause Driven Improvement', shortName: 'Root-Cause Improvement' },
  { name: 'Security & Privacy by Design', shortName: 'Security & Privacy' },
  { name: 'Observability & Telemetry', shortName: 'Observability' },
  { name: 'Maintainability & Sustainable Pace', shortName: 'Maintainability' }
]

function Scorecard({ project, onUpdate }) {
  const [scorecard, setScorecard] = useState(project.scorecard || {})
  const [evidence, setEvidence] = useState({})

  const handleStatusChange = (pillar, status) => {
    setScorecard({ ...scorecard, [pillar]: status })
  }

  const handleEvidenceChange = (pillar, text) => {
    setEvidence({ ...evidence, [pillar]: text })
  }

  const handleSave = async () => {
    const entries = PILLARS.map(p => ({
      pillar: p.shortName,
      status: scorecard[p.shortName] || '•',
      evidence: evidence[p.shortName] || ''
    }))
    await onUpdate(entries)
  }

  return (
    <div>
      <div className="scorecard">
        {PILLARS.map((pillar) => (
          <div key={pillar.shortName} className="pillar-section">
            <h3>{pillar.name}</h3>
            <p style={{ fontSize: '12px', color: '#999', marginBottom: '15px' }}>
              {pillar.shortName}
            </p>

            <div className="status-selector">
              {['✅', '⚠️', '❌', 'N/A'].map((status) => (
                <button
                  key={status}
                  className={`status-btn ${status === '✅' ? 'met' : status === '⚠️' ? 'partial' : status === '❌' ? 'gap' : ''} ${scorecard[pillar.shortName] === status ? 'selected' : ''}`}
                  onClick={() => handleStatusChange(pillar.shortName, status)}
                >
                  {status} {status === '✅' ? 'Met' : status === '⚠️' ? 'Partial' : status === '❌' ? 'Gap' : 'N/A'}
                </button>
              ))}
            </div>

            <textarea
              placeholder="Evidence or notes..."
              value={evidence[pillar.shortName] || ''}
              onChange={(e) => handleEvidenceChange(pillar.shortName, e.target.value)}
              style={{ marginTop: '10px', minHeight: '60px' }}
            />
          </div>
        ))}
      </div>

      <button onClick={handleSave} style={{ marginTop: '20px' }}>Save Scorecard</button>
    </div>
  )
}

export default Scorecard
