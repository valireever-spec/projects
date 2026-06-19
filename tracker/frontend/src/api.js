import axios from 'axios'

const API = axios.create({
  baseURL: '/api'
})

export const getProjects = () => API.get('/projects')
export const getProject = (id) => API.get(`/projects/${id}`)
export const createProject = (data) => API.post('/projects', data)
export const updateScorecard = (projectId, data) => API.put(`/projects/${projectId}/scorecard`, data)
export const createGap = (projectId, data) => API.post(`/projects/${projectId}/gaps`, data)
export const updateGap = (projectId, gapId, data) => API.put(`/projects/${projectId}/gaps/${gapId}`, data)
export const deleteGap = (projectId, gapId) => API.delete(`/projects/${projectId}/gaps/${gapId}`)
export const suggestRequirementsForGap = (projectId, gapId) => API.get(`/projects/${projectId}/gaps/${gapId}/suggest-requirements`)
export const linkRequirementToGap = (projectId, gapId, data) => API.put(`/projects/${projectId}/gaps/${gapId}/link-requirement`, data)
export const getLinkedGaps = (projectId, requirementId) => API.get(`/projects/${projectId}/requirements/${requirementId}/linked-gaps`)
export const getRequirementHealth = (projectId) => API.get(`/projects/${projectId}/requirement-health`)
export const getRules = () => API.get('/rules')
export const getPlaybooks = () => API.get('/playbooks')
export const getRequirements = (projectId) => API.get(`/projects/${projectId}/requirements`)
export const importRequirements = (projectId, projectPath) => API.post(`/projects/${projectId}/import-requirements`, { project_path: projectPath })
export const getRequirementsCoverage = (projectId) => API.get(`/projects/${projectId}/requirements-coverage`)
export const updateRequirement = (projectId, requirementId, data) => API.put(`/projects/${projectId}/requirements/${requirementId}`, data)
export const syncRequirementsToFiles = (projectId) => API.post(`/projects/${projectId}/sync-requirements`)
export const getSyncStatus = (projectId) => API.get(`/projects/${projectId}/sync-status`)
export const getPortfolioHealth = () => API.get('/portfolio/health')
export const getPortfolioByProject = () => API.get('/portfolio/by-project')
export const getPortfolioAtRisk = (limit = 20) => API.get('/portfolio/at-risk', { params: { limit } })
export const getPortfolioCategoryBreakdown = () => API.get('/portfolio/category-breakdown')
export const getPortfolioTypeBreakdown = () => API.get('/portfolio/type-breakdown')
export const getAutoImportStatus = () => API.get('/auto-import-status')

export default API
