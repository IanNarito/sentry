import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom'; // Added useNavigate
import { LayoutDashboard, Crosshair, Radio, Settings, Terminal, Shield, LogOut } from 'lucide-react'; // Added LogOut
import { useAuth } from '../context/AuthContext'; // Import Auth

const Layout = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth(); // Get logout function

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
    { name: 'Targets', path: '/targets', icon: <Crosshair size={20} /> },
    { name: 'Scans', path: '/scans', icon: <Radio size={20} /> },
    { name: 'Findings', path: '/findings', icon: <Shield size={20} /> },
    { name: 'Settings', path: '/settings', icon: <Settings size={20} /> },
  ];

  return (
    <div className="flex h-screen bg-background text-text font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-gray-800 bg-surface flex flex-col">
        <div className="p-6 flex items-center gap-3 border-b border-gray-800">
          <Terminal className="text-primary" size={28} />
          <h1 className="text-xl font-bold tracking-wider text-white">SENTRY</h1>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive 
                    ? 'bg-primary/10 text-primary border border-primary/20' 
                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                }`}
              >
                {item.icon}
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* LOGOUT SECTION */}
        <div className="p-4 border-t border-gray-800">
          <button 
            onClick={handleLogout}
            className="flex items-center gap-3 px-4 py-3 w-full rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-500/10 transition-all"
          >
            <LogOut size={20} />
            <span className="font-medium">Logout</span>
          </button>
          
          <div className="mt-4 bg-black/30 p-3 rounded border border-gray-800 text-xs text-gray-500 font-mono text-center">
            STATUS: ONLINE<br/>
            v1.0.0-release
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto bg-background relative">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f1f1f_1px,transparent_1px),linear-gradient(to_bottom,#1f1f1f_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none opacity-20"></div>
        <div className="relative z-10 p-8">
            {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;