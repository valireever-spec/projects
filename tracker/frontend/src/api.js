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
export const getRules = () => API.get('/rules')
export const getPlaybooks = () => API.get('/playbooks')

export default API
