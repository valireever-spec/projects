import { useState, useEffect } from 'react'
import { getRequirementHealth, getLinkedGaps } from '../api'

function RequirementHealth({ project }) {
  const [healthData, setHealthData] = useState([])
  const [loading, setLoading] = useState(true)
  const [expandedReq, setExpandedReq] = useState(null)
  const [linkedGaps, setLinkedGaps] = useState({})
  const [loadingGaps, setLoadingGaps] = useState({})

  useEffect(() => {
    fetchHealthData()
  }, [project.id])

  const fetchHealthData = async () => {
    setLoading(true)
    try {
      const { data } = await getRequirementHealth(project.id)
      setHealthData(data)
    } catch (err) {
      console.error('Failed to fetch health data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleExpandRequirement = async (reqId) => {
    setExpandedReq(expandedReq === reqId ? null : reqId)

    if (expandedReq !== reqId && !linkedGaps[reqId]) {
      setLoadingGaps({ ...loadingGaps, [reqId]: true })
      try {
        const { data } = await getLinkedGaps(project.id, reqId)
        setLinkedGaps({ ...linkedGaps, [reqId]: data })
      } catch (err) {
        console.error('Failed to fetch gaps:', err)
      } finally {
        setLoadingGaps({ ...loadingGaps, [reqId]: false })
      }
    }
  }

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'Critical': return '#ff4444'
      case 'High': return '#ff9800'
      case 'Low': return '#4CAF50'
      default: return '#999'
    }
  }

  const getHealthIcon = (health) => {
    switch (health) {
      case 'Healthy': return '✓'
      case 'At Risk': return '⚠'
      case 'Unvalidated': return '?'
      default: return '—'
    }
  }

  if (loading) {
    return <div style={{ color: '#999' }}>Loading requirement health...</div>
  }

  // Group by health status
  const healthy = healthData.filter(r => r.health === 'Healthy')
  const atRisk = healthData.filter(r => r.health === 'At Risk')
  const unvalidated = healthData.filter(r => r.health === 'Unvalidated')

  return (
    <div>
      <div style={{ marginBottom: '30px' }}>
        <h3 style={{ marginTop: 0 }}>Requirement Health Summary</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px', marginBottom: '30px' }}>
          <div style={{ padding: '15px', background: '#e8f5e9', borderRadius: '8px', borderLeft: '4px solid #4CAF50' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2e7d32' }}>
              {healthy.length}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>Healthy</div>
          </div>
          <div style={{ padding: '15px', background: '#fff3e0', borderRadius: '8px', borderLeft: '4px solid #ff9800' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#e65100' }}>
              {atRisk.length}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>At Risk</div>
          </div>
          <div style={{ padding: '15px', background: '#f5f5f5', borderRadius: '8px', borderLeft: '4px solid #999' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#666' }}>
              {unvalidated.length}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>Unvalidated</div>
          </div>
        </div>
      </div>

      {atRisk.length > 0 && (
        <div style={{ marginBottom: '30px' }}>
          <h4 style={{ color: '#ff9800', marginBottom: '15px' }}>⚠ At-Risk Requirements ({atRisk.length})</h4>
          {atRisk.map(req => (
            <div
              key={req.id}
              style={{
                border: `2px solid ${getRiskColor(req.risk_level)}`,
                borderRadius: '6px',
                padding: '15px',
                marginBottom: '12px',
                background: '#fff',
                cursor: 'pointer'
              }}
              onClick={() => handleExpandRequirement(req.id)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div>
                  <div style={{ fontWeight: 'bold', color: '#0066cc', marginBottom: '5px' }}>
                    {req.req_id}: {req.title}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666', display: 'flex', gap: '15px' }}>
                    <span>Type: {req.req_type}</span>
                    <span>Status: {req.status}</span>
                    <span>Criteria: {req.criteria_count}</span>
                    <span>Tests: {req.test_count}</span>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '14px', fontWeight: 'bold', color: getRiskColor(req.risk_level) }}>
                    {req.gap_count} {req.gap_count === 1 ? 'gap' : 'gaps'}
                  </div>
                  <div style={{ fontSize: '11px', color: '#999' }}>
                    Risk: {req.risk_level}
                  </div>
                </div>
              </div>

              {expandedReq === req.id && (
                <div style={{ marginTop: '15px', paddingTop: '15px', borderTop: '1px solid #eee' }}>
                  {loadingGaps[req.id] && <p style={{ color: '#999' }}>Loading linked gaps...</p>}
                  {!loadingGaps[req.id] && linkedGaps[req.id] && linkedGaps[req.id].length > 0 && (
                    <div>
                      <h5 style={{ margin: '0 0 10px 0', color: '#333' }}>Linked Gaps/Bugs:</h5>
                      {linkedGaps[req.id].map((gap, idx) => (
                        <div
                          key={idx}
                          style={{
                            background: '#f9f9f9',
                            padding: '10px',
                            borderRadius: '4px',
                            marginBottom: '8px',
                            fontSize: '12px'
                          }}
                        >
                          <div style={{ fontWeight: 'bold', color: '#333', marginBottom: '4px' }}>
                            {gap.title}
                          </div>
                          <div style={{ color: '#666', fontSize: '11px' }}>
                            Status: {gap.status} | Severity: {gap.severity} | Effort: {gap.effort}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  {!loadingGaps[req.id] && linkedGaps[req.id] && linkedGaps[req.id].length === 0 && (
                    <p style={{ color: '#999', fontSize: '12px' }}>No gaps linked yet</p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {healthy.length > 0 && (
        <div>
          <h4 style={{ color: '#4CAF50', marginBottom: '15px' }}>✓ Healthy Requirements ({healthy.length})</h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '12px' }}>
            {healthy.map(req => (
              <div
                key={req.id}
                style={{
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  padding: '12px',
                  background: '#f9f9f9'
                }}
              >
                <div style={{ fontWeight: 'bold', color: '#0066cc', marginBottom: '5px', fontSize: '14px' }}>
                  {req.req_id}
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>
                  {req.title}
                </div>
                <div style={{ fontSize: '11px', color: '#999', marginTop: '8px' }}>
                  Criteria: {req.criteria_count} | Tests: {req.test_count}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default RequirementHealth
