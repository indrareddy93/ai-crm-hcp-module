import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/log" replace />} />
        <Route path="log" element={<Home />} />
        <Route path="*" element={<Navigate to="/log" replace />} />
      </Route>
    </Routes>
  )
}
