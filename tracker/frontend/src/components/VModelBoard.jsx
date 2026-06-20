import { useState, useEffect } from 'react'
import API from '../api'

function VModelBoard({ project }) {
  const [vmodel, setVmodel] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchVModel()
  }, [project?.id])

  const fetchVModel = async () => {
    try {
      const { data } = await API.get(`/projects/${project.id}`)
      setVmodel(data)
    } catch (err) {
      console.error('Failed to fetch V-Model:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <p>Loading V-Model...</p>
  if (!vmodel) return <p>No V-Model data available</p>

  const requirements = vmodel.requirements || []
  const gaps = vmodel.gaps || []
  const validatedCount = requirements.filter(r => r.status === 'Validated').length
  const coverage = requirements.length > 0 ? ((validatedCount / requirements.length) * 100).toFixed(1) : 0

  const getSeverityColor = (severity) => {
    const colors = {
      Critical: '#ff4444',
      High: '#ff9900',
      Medium: '#ffcc00',
      Low: '#0099ff'
    }
    return colors[severity] || '#999'
  }

  const getStatusEmoji = (status) => {
    const emojis = {
      'Validated': '✅',
      'Implemented': '✔️',
      'Accepted': '📋',
      'Proposed': '📝'
    }
    return emojis[status] || '•'
  }

  return (
    <div style={{ padding: '20px', background: '#f5f5f5', borderRadius: '8px' }}>
      {/* Header with metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '15px', marginBottom: '30px' }}>
        <div style={{ background: '#fff', padding: '15px', borderRadius: '6px', border: '1px solid #ddd' }}>
          <div style={{ fontSize: '12px', color: '#999', marginBottom: '5px' }}>Coverage</div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#0066cc' }}>{coverage}%</div>
          <div style={{ fontSize: '11px', color: '#999', marginTop: '5px' }}>({validatedCount}/{requirements.length} validated)</div>
        </div>

        <div style={{ background: '#fff', padding: '15px', borderRadius: '6px', border: '1px solid #ddd' }}>
          <div style={{ fontSize: '12px', color: '#999', marginBottom: '5px' }}>Requirements</div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#0066cc' }}>{requirements.length}</div>
          <div style={{ fontSize: '11px', color: '#999', marginTop: '5px' }}>Total</div>
        </div>

        <div style={{ background: '#fff', padding: '15px', borderRadius: '6px', border: '1px solid #ddd' }}>
          <div style={{ fontSize: '12px', color: '#999', marginBottom: '5px' }}>Open Bugs</div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#ff4444' }}>{gaps.length}</div>
          <div style={{ fontSize: '11px', color: '#999', marginTop: '5px' }}>Gaps Found</div>
        </div>

        <div style={{ background: '#fff', padding: '15px', borderRadius: '6px', border: '1px solid #ddd' }}>
          <div style={{ fontSize: '12px', color: '#999', marginBottom: '5px' }}>Maturity</div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#0066cc' }}>{project.maturity_score || 0}%</div>
          <div style={{ fontSize: '11px', color: '#999', marginTop: '5px' }}>Score</div>
        </div>
      </div>

      {/* Requirements Section */}
      <div style={{ marginBottom: '30px' }}>
        <h3 style={{ marginBottom: '15px', color: '#333' }}>📋 Requirements</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '12px' }}>
          {requirements.map(req => (
            <div key={req.id} style={{ background: '#fff', padding: '12px', borderRadius: '6px', border: '1px solid #ddd' }}>
              <div style={{ fontWeight: '600', marginBottom: '5px', color: '#333' }}>
                {getStatusEmoji(req.status)} {req.req_id || req.id}
              </div>
              <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>{req.description}</div>
              <div style={{ fontSize: '11px', color: '#999' }}>Status: {req.status}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Bugs/Gaps Section */}
      <div>
        <h3 style={{ marginBottom: '15px', color: '#333' }}>🐛 Bugs & Gaps</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '12px' }}>
          {gaps.map(gap => (
            <div
              key={gap.id}
              style={{
                background: '#fff',
                padding: '12px',
                borderRadius: '6px',
                border: `2px solid ${getSeverityColor(gap.severity)}`,
                borderLeft: `4px solid ${getSeverityColor(gap.severity)}`
              }}
            >
              <div style={{ fontWeight: '600', marginBottom: '5px', color: '#333' }}>
                {gap.title}
              </div>
              <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>{gap.description}</div>
              <div style={{ display: 'flex', gap: '10px', fontSize: '11px', color: '#999' }}>
                <span style={{ color: getSeverityColor(gap.severity), fontWeight: '600' }}>
                  {gap.severity}
                </span>
                <span>{gap.status}</span>
              </div>
            </div>
          ))}
          {gaps.length === 0 && <p style={{ color: '#999' }}>No open gaps</p>}
        </div>
      </div>
    </div>
  )
}

export default VModelBoard
