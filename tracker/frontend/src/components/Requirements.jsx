import { useState, useEffect } from 'react'
import { getRequirements, importRequirements, getRequirementsCoverage, updateRequirement, syncRequirementsToFiles, getSyncStatus } from '../api'

function Requirements({ project }) {
  const [requirements, setRequirements] = useState([])
  const [coverage, setCoverage] = useState(null)
  const [loading, setLoading] = useState(false)
  const [importing, setImporting] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [expandedReq, setExpandedReq] = useState(null)
  const [editingReq, setEditingReq] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [activeFilter, setActiveFilter] = useState('all')
  const [syncStatus, setSyncStatus] = useState(null)

  useEffect(() => {
    fetchRequirements()
    fetchCoverage()
    fetchSyncStatus()
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

  const fetchCoverage = async () => {
    try {
      const { data } = await getRequirementsCoverage(project.id)
      setCoverage(data)
    } catch (err) {
      console.error('Failed to fetch coverage:', err)
    }
  }

  const fetchSyncStatus = async () => {
    try {
      const { data } = await getSyncStatus(project.id)
      setSyncStatus(data)
    } catch (err) {
      console.error('Failed to fetch sync status:', err)
    }
  }

  const handleImport = async () => {
    setImporting(true)
    try {
      await importRequirements(project.id, project.path)
      await fetchRequirements()
      await fetchCoverage()
      await fetchSyncStatus()
    } catch (err) {
      console.error('Failed to import requirements:', err)
    } finally {
      setImporting(false)
    }
  }

  const handleSync = async () => {
    setSyncing(true)
    try {
      await syncRequirementsToFiles(project.id)
      await fetchSyncStatus()
      alert('Requirements synced to project files successfully!')
    } catch (err) {
      console.error('Failed to sync requirements:', err)
      alert('Failed to sync requirements: ' + err.message)
    } finally {
      setSyncing(false)
    }
  }

  const handleEditStart = (req) => {
    setEditingReq(req.id)
    setEditForm({
      title: req.title,
      category: req.category,
      status: req.status,
      description: req.description
    })
  }

  const handleEditCancel = () => {
    setEditingReq(null)
    setEditForm({})
  }

  const handleEditSave = async (req) => {
    try {
      await updateRequirement(project.id, req.id, editForm)
      await fetchRequirements()
      setEditingReq(null)
      setEditForm({})
    } catch (err) {
      console.error('Failed to update requirement:', err)
      alert('Failed to update requirement: ' + err.message)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'Validated': return '#4CAF50'
      case 'Implemented': return '#2196F3'
      case 'In Progress': return '#FF9800'
      case 'Proposed': return '#999'
      default: return '#666'
    }
  }

  const filteredReqs = requirements.filter(req => {
    if (activeFilter === 'all') return true
    if (activeFilter === 'functional') return req.req_type === 'Functional'
    if (activeFilter === 'nonfunctional') return req.req_type === 'Non-Functional'
    if (activeFilter === 'gaps') return req.gap_count > 0
    return true
  })

  return (
    <div>
      {coverage && (
        <div style={{ marginBottom: '30px', padding: '20px', background: '#f5f5f5', borderRadius: '8px' }}>
          <h3 style={{ margin: '0 0 15px 0' }}>Requirements Coverage</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px' }}>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0066cc' }}>
                {coverage.overall_coverage}
              </div>
              <div style={{ fontSize: '12px', color: '#999' }}>Overall Coverage</div>
              <div style={{ fontSize: '11px', color: '#666' }}>
                {coverage.total_met}/{coverage.total_requirements} requirements met
              </div>
            </div>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2196F3' }}>
                {coverage.functional_coverage}
              </div>
              <div style={{ fontSize: '12px', color: '#999' }}>Functional (F)</div>
              <div style={{ fontSize: '11px', color: '#666' }}>
                {coverage.functional_met}/{coverage.functional_total} met
              </div>
            </div>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#FF9800' }}>
                {coverage.nonfunctional_coverage}
              </div>
              <div style={{ fontSize: '12px', color: '#999' }}>Non-Functional (NF)</div>
              <div style={{ fontSize: '11px', color: '#666' }}>
                {coverage.nonfunctional_met}/{coverage.nonfunctional_total} met
              </div>
            </div>
          </div>
        </div>
      )}

      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
        <button
          onClick={handleImport}
          disabled={importing}
          style={{
            background: importing ? '#ccc' : '#0066cc',
            color: '#fff',
            border: 'none',
            padding: '10px 15px',
            borderRadius: '4px',
            cursor: importing ? 'not-allowed' : 'pointer',
            fontWeight: 'bold'
          }}
        >
          {importing ? 'Importing...' : 'Import from Project'}
        </button>
        <button
          onClick={handleSync}
          disabled={syncing || requirements.length === 0}
          style={{
            background: syncing || requirements.length === 0 ? '#ccc' : '#4CAF50',
            color: '#fff',
            border: 'none',
            padding: '10px 15px',
            borderRadius: '4px',
            cursor: syncing || requirements.length === 0 ? 'not-allowed' : 'pointer',
            fontWeight: 'bold'
          }}
        >
          {syncing ? 'Syncing...' : 'Sync to Files'}
        </button>
        <span style={{ color: '#999', fontSize: '12px' }}>
          {requirements.length} requirement{requirements.length !== 1 ? 's' : ''} loaded
        </span>
        {syncStatus && syncStatus.synced && (
          <span style={{ color: '#4CAF50', fontSize: '12px', fontWeight: 'bold' }}>
            ✓ Synced with project files
          </span>
        )}
      </div>

      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <button
          onClick={() => setActiveFilter('all')}
          style={{
            background: activeFilter === 'all' ? '#0066cc' : '#f0f0f0',
            color: activeFilter === 'all' ? '#fff' : '#333',
            border: 'none',
            padding: '8px 12px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px'
          }}
        >
          All ({requirements.length})
        </button>
        <button
          onClick={() => setActiveFilter('functional')}
          style={{
            background: activeFilter === 'functional' ? '#2196F3' : '#f0f0f0',
            color: activeFilter === 'functional' ? '#fff' : '#333',
            border: 'none',
            padding: '8px 12px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px'
          }}
        >
          Functional ({requirements.filter(r => r.req_type === 'Functional').length})
        </button>
        <button
          onClick={() => setActiveFilter('nonfunctional')}
          style={{
            background: activeFilter === 'nonfunctional' ? '#FF9800' : '#f0f0f0',
            color: activeFilter === 'nonfunctional' ? '#fff' : '#333',
            border: 'none',
            padding: '8px 12px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px'
          }}
        >
          Non-Functional ({requirements.filter(r => r.req_type === 'Non-Functional').length})
        </button>
        <button
          onClick={() => setActiveFilter('gaps')}
          style={{
            background: activeFilter === 'gaps' ? '#ff4444' : '#f0f0f0',
            color: activeFilter === 'gaps' ? '#fff' : '#333',
            border: 'none',
            padding: '8px 12px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px'
          }}
        >
          With Gaps ({requirements.filter(r => r.gap_count > 0).length})
        </button>
      </div>

      {loading ? (
        <p style={{ color: '#999' }}>Loading requirements...</p>
      ) : filteredReqs.length === 0 ? (
        <p style={{ color: '#999' }}>
          {requirements.length === 0
            ? 'No requirements imported yet. Click "Import from Project" to load requirements.'
            : 'No requirements match the selected filter.'}
        </p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {filteredReqs.map(req => (
            editingReq === req.id ? (
              // Edit Mode
              <div
                key={req.id}
                style={{
                  border: '2px solid #0066cc',
                  borderRadius: '4px',
                  padding: '20px',
                  background: '#f9f9f9'
                }}
              >
                <h4 style={{ margin: '0 0 15px 0', color: '#0066cc' }}>Edit Requirement</h4>
                <div style={{ marginBottom: '12px' }}>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 'bold', marginBottom: '5px', color: '#333' }}>
                    Title
                  </label>
                  <input
                    type="text"
                    value={editForm.title}
                    onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '14px',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '12px', fontWeight: 'bold', marginBottom: '5px', color: '#333' }}>
                      Category
                    </label>
                    <input
                      type="text"
                      value={editForm.category}
                      onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '14px',
                        boxSizing: 'border-box'
                      }}
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '12px', fontWeight: 'bold', marginBottom: '5px', color: '#333' }}>
                      Status
                    </label>
                    <select
                      value={editForm.status}
                      onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '14px',
                        boxSizing: 'border-box'
                      }}
                    >
                      <option value="Proposed">Proposed</option>
                      <option value="Accepted">Accepted</option>
                      <option value="Implemented">Implemented</option>
                      <option value="Validated">Validated</option>
                    </select>
                  </div>
                </div>
                <div style={{ marginBottom: '15px' }}>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 'bold', marginBottom: '5px', color: '#333' }}>
                    Description
                  </label>
                  <textarea
                    value={editForm.description}
                    onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '14px',
                      boxSizing: 'border-box',
                      minHeight: '100px',
                      fontFamily: 'monospace'
                    }}
                  />
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    onClick={() => handleEditSave(req)}
                    style={{
                      background: '#4CAF50',
                      color: '#fff',
                      border: 'none',
                      padding: '8px 15px',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontWeight: 'bold'
                    }}
                  >
                    Save
                  </button>
                  <button
                    onClick={handleEditCancel}
                    style={{
                      background: '#999',
                      color: '#fff',
                      border: 'none',
                      padding: '8px 15px',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontWeight: 'bold'
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              // View Mode
              <div
                key={req.id}
                style={{
                  border: '1px solid #ddd',
                  borderLeft: `4px solid ${getStatusColor(req.status)}`,
                  borderRadius: '4px',
                  padding: '15px',
                  background: '#fff'
                }}
              >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', cursor: 'pointer' }}
                onClick={() => setExpandedReq(expandedReq === req.id ? null : req.id)}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '5px' }}>
                    <span style={{ fontWeight: 'bold', color: '#0066cc', fontSize: '14px' }}>
                      {req.req_id}
                    </span>
                    <span style={{ fontSize: '11px', background: req.req_type === 'Functional' ? '#e3f2fd' : '#fff3e0', padding: '2px 8px', borderRadius: '3px', color: req.req_type === 'Functional' ? '#1976d2' : '#f57c00' }}>
                      {req.req_type}
                    </span>
                    <span style={{ fontSize: '11px', background: '#f5f5f5', padding: '2px 8px', borderRadius: '3px', color: '#666' }}>
                      {req.category}
                    </span>
                    <span style={{ fontSize: '11px', fontWeight: 'bold', color: getStatusColor(req.status) }}>
                      {req.status}
                    </span>
                  </div>
                  <div style={{ fontSize: '15px', fontWeight: 'bold', marginBottom: '5px' }}>
                    {req.title}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {req.description?.substring(0, 100)}...
                  </div>
                </div>
                <div style={{ textAlign: 'right', marginLeft: '20px' }}>
                  {req.gap_count > 0 && (
                    <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#ff4444', marginBottom: '8px' }}>
                      {req.gap_count} {req.gap_count === 1 ? 'gap' : 'gaps'}
                    </div>
                  )}
                  <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleEditStart(req)
                      }}
                      style={{
                        background: '#2196F3',
                        color: '#fff',
                        border: 'none',
                        padding: '4px 10px',
                        borderRadius: '3px',
                        cursor: 'pointer',
                        fontSize: '11px',
                        fontWeight: 'bold'
                      }}
                    >
                      Edit
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setExpandedReq(expandedReq === req.id ? null : req.id)
                      }}
                      style={{
                        background: 'transparent',
                        color: '#999',
                        border: 'none',
                        padding: '4px 8px',
                        cursor: 'pointer',
                        fontSize: '11px'
                      }}
                    >
                      {expandedReq === req.id ? '▼' : '▶'} Details
                    </button>
                  </div>
                </div>
              </div>

              {expandedReq === req.id && (
                <div style={{ marginTop: '15px', paddingTop: '15px', borderTop: '1px solid #eee' }}>
                  {req.description && (
                    <div style={{ marginBottom: '12px' }}>
                      <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#333', marginBottom: '5px' }}>
                        Description
                      </div>
                      <div style={{ fontSize: '12px', color: '#666', whiteSpace: 'pre-wrap' }}>
                        {req.description}
                      </div>
                    </div>
                  )}

                  {req.measurement_method && (
                    <div style={{ marginBottom: '12px' }}>
                      <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#333', marginBottom: '5px' }}>
                        Measurement Method
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        {req.measurement_method}
                      </div>
                    </div>
                  )}

                  {req.target && (
                    <div style={{ marginBottom: '12px' }}>
                      <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#333', marginBottom: '5px' }}>
                        Target
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        {req.target}
                      </div>
                    </div>
                  )}

                  {req.acceptance_criteria && (
                    <div style={{ marginBottom: '12px' }}>
                      <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#333', marginBottom: '5px' }}>
                        Acceptance Criteria
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        {Array.isArray(req.acceptance_criteria) ? (
                          <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                            {req.acceptance_criteria.map((criterion, idx) => (
                              <li key={idx} style={{ marginBottom: '3px' }}>
                                {typeof criterion === 'string' ? criterion : criterion.description || JSON.stringify(criterion)}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <div>{req.acceptance_criteria}</div>
                        )}
                      </div>
                    </div>
                  )}

                  {req.test_case && (
                    <div style={{ marginBottom: '12px' }}>
                      <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#333', marginBottom: '5px' }}>
                        Test Cases
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        {Array.isArray(req.test_case) ? (
                          <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                            {req.test_case.map((test, idx) => (
                              <li key={idx} style={{ marginBottom: '3px' }}>
                                <code style={{ background: '#f5f5f5', padding: '2px 5px', borderRadius: '3px' }}>
                                  {test}
                                </code>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <code style={{ background: '#f5f5f5', padding: '2px 5px', borderRadius: '3px' }}>
                            {req.test_case}
                          </code>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Requirements
