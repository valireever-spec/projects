import { useState, useEffect } from 'react'
import { getRequirements } from '../api'

function Requirements({ project }) {
  const [requirements, setRequirements] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchRequirements()
  }, [project.id])

  const fetchRequirements = async () => {
    setLoading(true)
    try {
      const { data } = await getRequirements(project.id)
      setRequirements(data)
    } catch (err) {
      console.error('Failed to fetch requirements:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h3>Requirements</h3>
      {loading ? (
        <p>Loading requirements...</p>
      ) : requirements.length === 0 ? (
        <p>No requirements imported yet.</p>
      ) : (
        <div>
          <p>{requirements.length} requirement{requirements.length !== 1 ? 's' : ''} loaded</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {requirements.map(req => (
              <div
                key={req.id}
                style={{
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  padding: '12px',
                  background: '#fff'
                }}
              >
                <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#0066cc' }}>
                  {req.req_id} — {req.title}
                </div>
                <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                  {req.req_type} · {req.status}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Requirements
