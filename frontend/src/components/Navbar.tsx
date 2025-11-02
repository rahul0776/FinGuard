import { Link } from 'react-router-dom';
import { Shield } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="bg-slate-800 border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link to="/" className="flex items-center">
              <Shield className="h-8 w-8 text-red-500" />
              <span className="ml-2 text-xl font-bold text-white">FinGuard</span>
            </Link>
            <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
              <Link
                to="/demo"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-300 hover:text-white"
              >
                Live Demo
              </Link>
              <Link
                to="/replay"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-300 hover:text-white"
              >
                Replay
              </Link>
              <Link
                to="/about"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-300 hover:text-white"
              >
                About
              </Link>
            </div>
          </div>
          <div className="flex items-center">
            <span className="text-xs text-gray-400">Real-Time Fraud Detection</span>
          </div>
        </div>
      </div>
    </nav>
  );
}



