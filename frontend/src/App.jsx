// frontend/src/App.jsx
import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'; // NEW IMPORTS
import Dashboard from './Dashboard'; // NEW IMPORT
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const checkLoginStatus = async () => {
    try {
      setError(null);
      const response = await fetch('/api/user/me');
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else if (response.status === 401) {
        setUser(null);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch user data');
      }
    } catch (err) {
      console.error("Error checking login status:", err);
      setError(err.message);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = () => {
    window.location.href = '/api/auth/login';
  };

  const handleLogout = async () => {
    try {
      const response = await fetch('/api/auth/logout', { method: 'POST' });
      if (response.ok) {
        setUser(null);
        // After logout, React Router will handle redirect back to '/' if user is null
      } else {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Logout failed');
      }
    } catch (err) {
      console.error("Error during logout:", err);
      setError(err.message);
    }
  };

  useEffect(() => {
    checkLoginStatus();
  }, []);

  if (loading) {
    return (
      <div className="App">
        <header className="App-header">
          <h1>CognitoSphere</h1>
          <p>Loading...</p>
        </header>
      </div>
    );
  }

  // Main application rendering with Router
  return (
    <Router>
      <Routes>
        <Route path="/" element={
          <div className="App">
            <header className="App-header">
              {user ? (
                // If user is logged in, redirect to dashboard
                <Navigate to="/dashboard" replace />
              ) : (
                // If not logged in, show login section
                <div className="login-section">
                  <h1>Welcome to CognitoSphere!</h1>
                  <p>Your Hyper-Personalized Cognitive Augmentation System.</p>
                  {error && <p className="error-message">Login Error: {error}</p>}
                  <button onClick={handleLogin}>Login with Google</button>
                </div>
              )}
            </header>
          </div>
        } />

        <Route path="/dashboard" element={
          user ? (
            <Dashboard user={user} onLogout={handleLogout} />
          ) : (
            // If trying to access dashboard but not logged in, redirect to home
            <Navigate to="/" replace />
          )
        } />

        {/* Catch-all for 404s */}
        <Route path="*" element={
          <div className="App">
            <header className="App-header">
              <h1>404: Page Not Found</h1>
              <p>The page you are looking for does not exist.</p>
              <a href="/">Go to Home</a>
            </header>
          </div>
        } />
      </Routes>
    </Router>
  );
}

export default App;