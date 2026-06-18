import { useState, useEffect } from 'react'
import { getRules, getPlaybooks } from '../api'

function Rules({ project }) {
  const [rulesData, setRulesData] = useState(null)
  const [playbooksData, setPlaybooksData] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetchFrameworkData()
  }, [])

  const fetchFrameworkData = async () => {
    try {
      const [rulesRes, playbooksRes] = await Promise.all([getRules(), getPlaybooks()])
      setRulesData(rulesRes.data)
      setPlaybooksData(playbooksRes.data)
    } catch (err) {
      console.error('Failed to fetch framework data:', err)
    }
  }

  return (
    <div>
      <div className="card" style={{ marginBottom: '20px' }}>
        <h3>Framework Reference</h3>
        <p style={{ fontSize: '13px', color: '#666', marginTop: '10px' }}>
          Search and reference the 8-pillar architecture validation framework.
        </p>

        <input
          type="text"
          placeholder="Search rules by pillar or keyword..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ marginTop: '10px' }}
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div className="card">
          <h3>48 Rules</h3>
          {rulesData?.status === 'loaded' ? (
            <p style={{ fontSize: '13px' }}>
              ✅ Framework rules loaded ({rulesData.rules_count} rules found)
            </p>
          ) : (
            <p style={{ fontSize: '13px', color: '#999' }}>
              Loading rules from project-designer/FRAMEWORK.md...
            </p>
          )}
          <p style={{ fontSize: '12px', color: '#666', marginTop: '10px' }}>
            Reference the 6 rules per pillar with verification methods and test scenarios.
          </p>
        </div>

        <div className="card">
          <h3>Playbooks</h3>
          {playbooksData?.status === 'loaded' ? (
            <p style={{ fontSize: '13px' }}>
              ✅ Playbooks loaded ({playbooksData.playbooks_count} playbooks found)
            </p>
          ) : (
            <p style={{ fontSize: '13px', color: '#999' }}>
              Loading playbooks from project-designer/PLAYBOOKS.md...
            </p>
          )}
          <p style={{ fontSize: '12px', color: '#666', marginTop: '10px' }}>
            Step-by-step guides for fixing common gaps (FastAPI + Python focused).
          </p>
        </div>
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <h3>Gap Remediation Resources</h3>
        <p style={{ fontSize: '13px', marginTop: '10px' }}>
          For each gap or bug logged in your Kanban board, find relevant rules and playbooks:
        </p>
        <ul style={{ marginTop: '10px', fontSize: '13px', lineHeight: '1.6' }}>
          <li>Identify which pillar the gap falls under</li>
          <li>Reference the 6 rules for that pillar in FRAMEWORK.md</li>
          <li>Check PLAYBOOKS.md for step-by-step implementation guides</li>
          <li>Log progress as gaps move through the Kanban board</li>
        </ul>
      </div>
    </div>
  )
}

export default Rules
