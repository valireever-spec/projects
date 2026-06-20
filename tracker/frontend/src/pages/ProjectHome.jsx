import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getProject, updateScorecard, createGap, updateGap, deleteGap } from '../api'
import Scorecard from '../components/Scorecard'
import GapsBoard from '../components/GapsBoard'
import Rules from '../components/Rules'
import Requirements from '../components/Requirements'
import RequirementHealth from '../components/RequirementHealth'
import VModelBoard from '../components/VModelBoard'

function ProjectHome() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [activeTab, setActiveTab] = useState('scorecard')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProject()
  }, [id])

  const fetchProject = async () => {
    try {
      const { data } = await getProject(id)
      setProject(data)
    } catch (err) {
      console.error('Failed to fetch project:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleScorecardUpdate = async (scorecard) => {
    try {
      await updateScorecard(id, scorecard)
      fetchProject()
    } catch (err) {
      console.error('Failed to update scorecard:', err)
    }
  }

  const handleGapCreate = async (gap) => {
    try {
      await createGap(id, gap)
      fetchProject()
    } catch (err) {
      console.error('Failed to create gap:', err)
    }
  }

  const handleGapUpdate = async (gapId, gap) => {
    try {
      await updateGap(id, gapId, gap)
      fetchProject()
    } catch (err) {
      console.error('Failed to update gap:', err)
    }
  }

  const handleGapDelete = async (gapId) => {
    try {
      await deleteGap(id, gapId)
      fetchProject()
    } catch (err) {
      console.error('Failed to delete gap:', err)
    }
  }

  if (loading) return <div className="container"><p>Loading...</p></div>
  if (!project) return <div className="container"><p>Project not found</p></div>

  return (
    <div>
      <div className="header" style={{ background: '#0066cc', color: '#fff', paddingBottom: '15px' }}>
        <div className="container">
          <button onClick={() => navigate('/')} style={{ background: 'rgba(255,255,255,0.2)', color: '#fff', marginBottom: '10px' }}>← Back</button>
          <h1 style={{ color: '#fff' }}>{project.name}</h1>
          {project.tech_stack && <p style={{ color: 'rgba(255,255,255,0.8)' }}>{project.tech_stack}</p>}
        </div>
      </div>

      <div className="container" style={{ marginTop: '30px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
          <div>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#0066cc' }}>
              {project.maturity_score}%
            </div>
            <div style={{ fontSize: '13px', color: '#999' }}>Maturity Score</div>
          </div>
          <div>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#ff9900' }}>
              {project.gaps?.length || 0}
            </div>
            <div style={{ fontSize: '13px', color: '#999' }}>Open Gaps</div>
          </div>
          <div>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#666' }}>
              {project.review_count || 0}
            </div>
            <div style={{ fontSize: '13px', color: '#999' }}>Reviews</div>
          </div>
        </div>

        <div className="nav">
          <button
            className={activeTab === 'scorecard' ? 'active' : ''}
            onClick={() => setActiveTab('scorecard')}
          >
            Scorecard
          </button>
          <button
            className={activeTab === 'gaps' ? 'active' : ''}
            onClick={() => setActiveTab('gaps')}
          >
            Gaps & Bugs
          </button>
          <button
            className={activeTab === 'requirements' ? 'active' : ''}
            onClick={() => setActiveTab('requirements')}
          >
            Requirements
          </button>
          <button
            className={activeTab === 'health' ? 'active' : ''}
            onClick={() => setActiveTab('health')}
          >
            Health & At-Risk
          </button>
          <button
            className={activeTab === 'rules' ? 'active' : ''}
            onClick={() => setActiveTab('rules')}
          >
            Rules & Playbooks
          </button>
          <button
            className={activeTab === 'vmodel' ? 'active' : ''}
            onClick={() => setActiveTab('vmodel')}
          >
            📊 V-Model Board
          </button>
        </div>

        <div style={{ marginTop: '30px' }}>
          {activeTab === 'scorecard' && (
            <Scorecard project={project} onUpdate={handleScorecardUpdate} />
          )}
          {activeTab === 'gaps' && (
            <GapsBoard
              project={project}
              gaps={project.gaps || []}
              onCreate={handleGapCreate}
              onUpdate={handleGapUpdate}
              onDelete={handleGapDelete}
            />
          )}
          {activeTab === 'requirements' && <Requirements project={project} />}
          {activeTab === 'health' && <RequirementHealth project={project} />}
          {activeTab === 'rules' && <Rules project={project} />}
          {activeTab === 'vmodel' && <VModelBoard project={project} />}
        </div>
      </div>
    </div>
  )
}

export default ProjectHome
