// frontend/src/Dashboard.jsx
import React from 'react';

function Dashboard({ user, onLogout }) { // Receive user and logout function as props
  if (!user) {
    // This case should ideally be handled by App.jsx, but good to have fallback
    return (
      <div className="dashboard-container">
        <h2>Not Logged In</h2>
        <p>Please log in to access the dashboard.</p>
        {/* You could add a redirect to login here if desired */}
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <h2>Welcome to your Dashboard, {user.name}!</h2>
      {user.picture && <img src={user.picture} alt="Profile" className="profile-picture" />}
      <p>This is where your personalized cognitive augmentation tools will live.</p>

      <div className="dashboard-features">
        <h3>Core Features:</h3>
        <ul>
          <li>Real-time Information Synthesis</li>
          <li>Logical Fallacy & Bias Identification</li>
          <li>Creative Solution Generation</li>
          <li>Personalized Cognitive Boosts</li>
        </ul>
      </div>

      <button onClick={onLogout}>Logout</button>
    </div>
  );
}

export default Dashboard;