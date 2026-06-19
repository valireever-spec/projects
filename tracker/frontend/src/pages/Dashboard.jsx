import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getProjects, createProject, getAutoImportStatus } from '../api'
import API from '../api'

function Dashboard() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [importing, setImporting] = useState(false)
  const [autoImportStatus, setAutoImportStatus] = useState(null)
  const [formData, setFormData] = useState({ name: '', tech_stack: '', description: '' })
  const navigate = useNavigate()

  const pillars = [
    'Architecture Discipline', 'Build Quality In', 'Verification & Validation',
    'CI & Safe Delivery', 'Root-Cause Improvement', 'Security & Privacy',
    'Observability', 'Maintainability'
  ]

  useEffect(() => {
    fetchProjects()
    fetchAutoImportStatus()
    // Refresh auto-import status every 30 seconds
    const interval = setInterval(fetchAutoImportStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchProjects = async () => {
    try {
      const { data } = await getProjects()
      setProjects(data)
    } catch (err) {
      console.error('Failed to fetch projects:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchAutoImportStatus = async () => {
    try {
      const { data } = await getAutoImportStatus()
      setAutoImportStatus(data)
    } catch (err) {
      console.error('Failed to fetch auto-import status:', err)
    }
  }

  const handleCreateProject = async (e) => {
    e.preventDefault()
    try {
      await createProject(formData)
      setFormData({ name: '', tech_stack: '', description: '' })
      setShowForm(false)
      fetchProjects()
    } catch (err) {
      console.error('Failed to create project:', err)
    }
  }

  const handleImportProjects = async () => {
    setImporting(true)
    try {
      const { data } = await API.post('/import-projects')
      fetchProjects()
      alert(`Imported ${data.imported} projects (${data.skipped} already tracked)`)
    } catch (err) {
      console.error('Failed to import projects:', err)
      alert('Failed to import projects')
    } finally {
      setImporting(false)
    }
  }

  const getStatusEmoji = (status) => {
    const map = { '✅': '✅', 'Met': '✅', '⚠️': '⚠️', 'Partial': '⚠️', '❌': '❌', 'Gap': '❌' }
    return map[status] || '•'
  }

  if (loading) return <div className="container"><p>Loading...</p></div>

  return (
    <div>
      {autoImportStatus && autoImportStatus.running && (
        <div style={{
          background: '#e8f5e9',
          borderBottom: '2px solid #4CAF50',
          padding: '12px 0',
          textAlign: 'center',
          fontSize: '12px',
          color: '#2e7d32',
          fontWeight: '500'
        }}>
          🔄 Auto-import active ({autoImportStatus.sync_count} syncs completed)
          {autoImportStatus.next_run && (
            <span style={{ marginLeft: '10px', opacity: 0.7 }}>
              Next sync: {new Date(autoImportStatus.next_run).toLocaleTimeString()}
            </span>
          )}
        </div>
      )}
      <div className="header">
        <div className="container">
          <h1>Design & Bug Tracker</h1>
          <p style={{ color: '#666', marginTop: '5px' }}>Track architecture reviews and gaps across your portfolio</p>
        </div>
      </div>

      <div className="container">
        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' }}>
          {!showForm && (
            <>
              <button onClick={() => setShowForm(true)}>
                + New Project
              </button>
              <button
                onClick={handleImportProjects}
                disabled={importing}
                style={{ background: '#666' }}
              >
                {importing ? 'Importing...' : '📦 Import from tracker.json'}
              </button>
              <button
                onClick={() => navigate('/portfolio')}
                style={{ background: '#0066cc' }}
              >
                📊 Portfolio Dashboard
              </button>
            </>
          )}
        </div>

        {showForm && (
          <div className="card" style={{ marginBottom: '20px' }}>
            <h3>New Project</h3>
            <form onSubmit={handleCreateProject}>
              <input
                type="text"
                placeholder="Project name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                style={{ marginBottom: '10px' }}
              />
              <input
                type="text"
                placeholder="Tech stack (e.g., Python, React)"
                value={formData.tech_stack}
                onChange={(e) => setFormData({ ...formData, tech_stack: e.target.value })}
                style={{ marginBottom: '10px' }}
              />
              <textarea
                placeholder="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                style={{ marginBottom: '10px', minHeight: '80px' }}
              />
              <div style={{ display: 'flex', gap: '10px' }}>
                <button type="submit">Create</button>
                <button type="button" onClick={() => setShowForm(false)} style={{ background: '#999' }}>Cancel</button>
              </div>
            </form>
          </div>
        )}

        <div className="grid grid-2">
          {projects.map((project) => (
            <div
              key={project.id}
              className="card"
              onClick={() => navigate(`/project/${project.id}`)}
            >
              <h3>{project.name}</h3>
              {project.tech_stack && <p><strong>Stack:</strong> {project.tech_stack}</p>}
              {project.description && <p>{project.description}</p>}

              <div style={{ marginTop: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0066cc' }}>
                    {project.maturity_score}%
                  </div>
                  <div style={{ fontSize: '11px', color: '#999' }}>Maturity</div>
                </div>

                <div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ff9900' }}>
                    {project.gap_count}
                  </div>
                  <div style={{ fontSize: '11px', color: '#999' }}>Gaps</div>
                </div>
              </div>

              <div className="pillars">
                {pillars.map((pillar) => (
                  <div
                    key={pillar}
                    className={`pill ${
                      project.pillar_status[pillar] === '✅' ? 'met' :
                      project.pillar_status[pillar] === '⚠️' ? 'partial' :
                      project.pillar_status[pillar] === '❌' ? 'gap' : ''
                    }`}
                    title={pillar}
                  >
                    {getStatusEmoji(project.pillar_status[pillar] || '•')}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
