import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import RootLayout from "./components/layout/RootLayout"
import Placeholder from "./pages/Placeholder"
import Login from "./pages/auth/Login"
import Register from "./pages/auth/Register"
import ForgotPassword from "./pages/auth/ForgotPassword"
import { AuthProvider } from "./contexts/AuthContext"
import ProtectedRoute from "./components/auth/ProtectedRoute"

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          
          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<RootLayout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Placeholder title="Dashboard" />} />
              
              {/* Future specialized routes with role protection */}
              <Route element={<ProtectedRoute allowedRoles={['ADMIN', 'GOVERNMENT']} />}>
                <Route path="labour-market" element={<Placeholder title="Labour Market Intelligence" />} />
                <Route path="districts" element={<Placeholder title="District Intelligence" />} />
              </Route>
              
              <Route path="skills" element={<Placeholder title="Skill Intelligence" />} />
              <Route path="curriculum" element={<Placeholder title="Curriculum Alignment" />} />
              <Route path="students" element={<Placeholder title="Student Development" />} />
              <Route path="training" element={<Placeholder title="Training Intelligence" />} />
              <Route path="agents" element={<Placeholder title="AI Agents Orchestration" />} />
              <Route path="settings" element={<Placeholder title="Settings" />} />
              <Route path="*" element={<Placeholder title="404 - Not Found" />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
