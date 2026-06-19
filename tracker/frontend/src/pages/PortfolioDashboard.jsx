import { useState, useEffect } from 'react'
import { getPortfolioHealth, getPortfolioByProject, getPortfolioAtRisk, getPortfolioCategoryBreakdown, getPortfolioTypeBreakdown } from '../api'

function PortfolioDashboard() {
  const [health, setHealth] = useState(null)
  const [byProject, setByProject] = useState([])
  const [atRisk, setAtRisk] = useState([])
  const [categoryBreakdown, setCategoryBreakdown] = useState({})
  const [typeBreakdown, setTypeBreakdown] = useState({})
  const [loading, setLoading] = useState(true)
  const [expandedProject, setExpandedProject] = useState(null)

  useEffect(() => {
    fetchPortfolioData()
  }, [])

  const fetchPortfolioData = async () => {
    setLoading(true)
    try {
      const [healthRes, projectRes, riskRes, catRes, typeRes] = await Promise.all([
        getPortfolioHealth(),
        getPortfolioByProject(),
        getPortfolioAtRisk(15),
        getPortfolioCategoryBreakdown(),
        getPortfolioTypeBreakdown()
      ])

      setHealth(healthRes.data)
      setByProject(projectRes.data)
      setAtRisk(riskRes.data)
      setCategoryBreakdown(catRes.data)
      setTypeBreakdown(typeRes.data)
    } catch (err) {
      console.error('Failed to fetch portfolio data:', err)
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 90) return '#4CAF50' // Green
    if (score >= 80) return '#8BC34A'
    if (score >= 70) return '#FFC107'
    if (score >= 60) return '#FF9800'
    return '#f44336' // Red
  }

  const getGrade = (score) => {
    if (score >= 90) return 'A'
    if (score >= 80) return 'B'
    if (score >= 70) return 'C'
    if (score >= 60) return 'D'
    return 'F'
  }

  if (loading) {
    return <div style={{ padding: '20px', color: '#999' }}>Loading portfolio data...</div>
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1400px', margin: '0 auto' }}>
      <h1 style={{ marginTop: 0, color: '#0066cc' }}>Portfolio Dashboard</h1>

      {health && (
        <div style={{ marginBottom: '40px' }}>
          <h2 style={{ marginTop: 0, marginBottom: '20px', color: '#333' }}>Portfolio Health</h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
            {/* Main Score Card */}
            <div style={{
              background: 'linear-gradient(135deg, #0066cc 0%, #0052a3 100%)',
              color: '#fff',
              borderRadius: '8px',
              padding: '30px',
              textAlign: 'center',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '10px' }}>
                {health.portfolio_score.score}%
              </div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '5px' }}>
                Grade: {health.portfolio_score.grade}
              </div>
              <div style={{ fontSize: '14px', opacity: 0.9 }}>
                {health.portfolio_score.status}
              </div>
            </div>

            {/* Coverage Card */}
            <div style={{
              background: '#e8f5e9',
              borderLeft: '4px solid #4CAF50',
              borderRadius: '8px',
              padding: '20px'
            }}>
              <div style={{ fontSize: '14px', color: '#999', marginBottom: '10px' }}>Coverage</div>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#2e7d32', marginBottom: '10px' }}>
                {health.coverage_percent}%
              </div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                {health.healthy} healthy / {health.total_requirements} total
              </div>
            </div>

            {/* At-Risk Card */}
            <div style={{
              background: '#fff3e0',
              borderLeft: '4px solid #ff9800',
              borderRadius: '8px',
              padding: '20px'
            }}>
              <div style={{ fontSize: '14px', color: '#999', marginBottom: '10px' }}>At-Risk</div>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#e65100', marginBottom: '10px' }}>
                {health.at_risk}
              </div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                {health.at_risk_percent}% of requirements
              </div>
            </div>

            {/* Gaps Card */}
            <div style={{
              background: '#ffebee',
              borderLeft: '4px solid #f44336',
              borderRadius: '8px',
              padding: '20px'
            }}>
              <div style={{ fontSize: '14px', color: '#999', marginBottom: '10px' }}>Open Gaps</div>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#c62828', marginBottom: '10px' }}>
                {health.total_gaps}
              </div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                {health.critical_risk_count} critical risk
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Type Breakdown */}
      {typeBreakdown.functional && (
        <div style={{ marginBottom: '40px' }}>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>Functional vs Non-Functional</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
            <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px' }}>
              <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '15px', color: '#0066cc' }}>
                Functional Requirements
              </div>
              <div style={{ marginBottom: '10px' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0066cc' }}>
                  {typeBreakdown.functional.coverage_percent}%
                </div>
                <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                  {typeBreakdown.functional.healthy} healthy / {typeBreakdown.functional.total} total
                </div>
              </div>
              <div style={{ display: 'flex', gap: '10px', fontSize: '12px', marginTop: '15px' }}>
                <span style={{ color: '#4CAF50' }}>✓ {typeBreakdown.functional.healthy}</span>
                <span style={{ color: '#ff9800' }}>⚠ {typeBreakdown.functional.at_risk}</span>
                <span style={{ color: '#999' }}>? {typeBreakdown.functional.unvalidated}</span>
              </div>
            </div>

            <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px' }}>
              <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '15px', color: '#ff9800' }}>
                Non-Functional Requirements
              </div>
              <div style={{ marginBottom: '10px' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ff9800' }}>
                  {typeBreakdown.nonfunctional.coverage_percent}%
                </div>
                <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                  {typeBreakdown.nonfunctional.healthy} healthy / {typeBreakdown.nonfunctional.total} total
                </div>
              </div>
              <div style={{ display: 'flex', gap: '10px', fontSize: '12px', marginTop: '15px' }}>
                <span style={{ color: '#4CAF50' }}>✓ {typeBreakdown.nonfunctional.healthy}</span>
                <span style={{ color: '#ff9800' }}>⚠ {typeBreakdown.nonfunctional.at_risk}</span>
                <span style={{ color: '#999' }}>? {typeBreakdown.nonfunctional.unvalidated}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* By Project */}
      {byProject.length > 0 && (
        <div style={{ marginBottom: '40px' }}>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>Projects at a Glance</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              border: '1px solid #ddd',
              borderRadius: '8px'
            }}>
              <thead>
                <tr style={{ background: '#f5f5f5' }}>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd', fontWeight: 'bold' }}>Project</th>
                  <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #ddd', fontWeight: 'bold' }}>Requirements</th>
                  <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #ddd', fontWeight: 'bold' }}>Coverage</th>
                  <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #ddd', fontWeight: 'bold' }}>Healthy</th>
                  <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #ddd', fontWeight: 'bold' }}>At-Risk</th>
                  <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #ddd', fontWeight: 'bold' }}>Gaps</th>
                  <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #ddd', fontWeight: 'bold' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {byProject.map((project) => (
                  <tr key={project.project_id} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '12px', color: '#0066cc', fontWeight: 'bold' }}>{project.project_name}</td>
                    <td style={{ padding: '12px', textAlign: 'center', color: '#666' }}>{project.total_requirements}</td>
                    <td style={{ padding: '12px', textAlign: 'center', fontWeight: 'bold', color: getScoreColor(project.coverage_percent) }}>
                      {project.coverage_percent}%
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center', color: '#4CAF50' }}>✓ {project.healthy}</td>
                    <td style={{ padding: '12px', textAlign: 'center', color: '#ff9800' }}>⚠ {project.at_risk}</td>
                    <td style={{ padding: '12px', textAlign: 'center', color: '#f44336' }}>{project.total_gaps}</td>
                    <td style={{
                      padding: '12px',
                      textAlign: 'center',
                      fontWeight: 'bold',
                      color: project.health_status === 'Healthy' ? '#4CAF50' : project.health_status === 'At Risk' ? '#ff9800' : '#f44336'
                    }}>
                      {project.health_status}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* At-Risk Requirements */}
      {atRisk.length > 0 && (
        <div style={{ marginBottom: '40px' }}>
          <h3 style={{ marginBottom: '20px', color: '#ff9800' }}>⚠ Top At-Risk Requirements</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {atRisk.map((req) => (
              <div
                key={req.req_id}
                style={{
                  border: '2px solid #ff9800',
                  borderRadius: '6px',
                  padding: '15px',
                  background: '#fff9f3',
                  cursor: 'pointer'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div>
                    <div style={{ fontWeight: 'bold', color: '#0066cc', marginBottom: '5px', fontSize: '15px' }}>
                      {req.req_id}: {req.title}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666', display: 'flex', gap: '15px' }}>
                      <span>{req.project_name}</span>
                      <span>Type: {req.req_type}</span>
                      <span>Status: {req.status}</span>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right', minWidth: '100px' }}>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#f44336', marginBottom: '5px' }}>
                      {req.gap_count} gaps
                    </div>
                    <div style={{ fontSize: '12px', color: '#ff9800', fontWeight: 'bold' }}>
                      Risk: {req.risk_level}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Category Breakdown */}
      {Object.keys(categoryBreakdown).length > 0 && (
        <div>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>Requirements by Category</h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
            gap: '15px'
          }}>
            {Object.entries(categoryBreakdown).map(([category, stats]) => (
              <div
                key={category}
                style={{
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  padding: '15px',
                  background: '#f9f9f9'
                }}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '10px', color: '#333', fontSize: '14px' }}>
                  {category}
                </div>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0066cc', marginBottom: '10px' }}>
                  {stats.total}
                </div>
                <div style={{ display: 'flex', gap: '8px', fontSize: '11px' }}>
                  <span style={{ color: '#4CAF50' }}>✓ {stats.healthy}</span>
                  <span style={{ color: '#ff9800' }}>⚠ {stats.at_risk}</span>
                  <span style={{ color: '#999' }}>? {stats.unvalidated}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default PortfolioDashboard
