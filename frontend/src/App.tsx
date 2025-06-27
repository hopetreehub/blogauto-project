import React from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import TitleGenerator from './pages/TitleGenerator';
import ContentGenerator from './pages/ContentGenerator';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import AuthPage from './pages/AuthPage';
import DomainSelector from './pages/DomainSelector';
import AdminPanel from './pages/AdminPanel';
import GuidelinesManager from './pages/GuidelinesManager';
import BlogAutomationHub from './pages/BlogAutomationHub';
import SiteManager from './pages/SiteManager';
import AutomationWorkflow from './pages/AutomationWorkflow';
import Sidebar from './components/Sidebar';
import ErrorBoundary from './components/ErrorBoundary';

function AppContent() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading">로딩 중...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthPage />;
  }

  return (
    <div className="App">
      <Sidebar />
      <main className="main-content">
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<BlogAutomationHub />} />
            <Route path="/index.html" element={<BlogAutomationHub />} />
            <Route path="/blog-automation-hub.html" element={<BlogAutomationHub />} />
            <Route path="/site-manager.html" element={<SiteManager />} />
            <Route path="/automation-workflow.html" element={<AutomationWorkflow />} />
            <Route path="/dashboard.html" element={<Dashboard />} />
            <Route path="/titles.html" element={<TitleGenerator />} />
            <Route path="/content.html" element={<ContentGenerator />} />
            <Route path="/admin.html" element={<AdminPanel />} />
            <Route path="/guidelines.html" element={<GuidelinesManager />} />
            <Route path="/settings.html" element={<Settings />} />
          </Routes>
        </ErrorBoundary>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;