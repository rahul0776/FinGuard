import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import AlertDetail from './pages/AlertDetail';
import Replay from './pages/Replay';
import About from './pages/About';
import Navbar from './components/Navbar';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-900 text-white">
        <Navbar />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/demo" element={<Dashboard />} />
          <Route path="/case/:alertId" element={<AlertDetail />} />
          <Route path="/replay" element={<Replay />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;



