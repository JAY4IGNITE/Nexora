import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import RootLayout from "./components/layout/RootLayout"
import Placeholder from "./pages/Placeholder"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RootLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Placeholder title="Dashboard" />} />
          <Route path="labour-market" element={<Placeholder title="Labour Market Intelligence" />} />
          <Route path="skills" element={<Placeholder title="Skill Intelligence" />} />
          <Route path="curriculum" element={<Placeholder title="Curriculum Alignment" />} />
          <Route path="districts" element={<Placeholder title="District Intelligence" />} />
          <Route path="students" element={<Placeholder title="Student Development" />} />
          <Route path="training" element={<Placeholder title="Training Intelligence" />} />
          <Route path="agents" element={<Placeholder title="AI Agents Orchestration" />} />
          <Route path="settings" element={<Placeholder title="Settings" />} />
          <Route path="*" element={<Placeholder title="404 - Not Found" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
