import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import ProjectHome from './pages/ProjectHome'
import PortfolioDashboard from './pages/PortfolioDashboard'
import './index.css'

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/portfolio" element={<PortfolioDashboard />} />
          <Route path="/project/:id" element={<ProjectHome />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
