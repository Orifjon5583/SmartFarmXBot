import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout.jsx';
import ProtectedRoute from './components/layout/ProtectedRoute.jsx';
import Analytics from './pages/Analytics.jsx';
import CameraMonitoring from './pages/CameraMonitoring.jsx';
import Dashboard from './pages/Dashboard.jsx';
import DeviceControl from './pages/DeviceControl.jsx';
import Login from './pages/Login.jsx';
import Settings from './pages/Settings.jsx';

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="devices" element={<DeviceControl />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="camera" element={<CameraMonitoring />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
