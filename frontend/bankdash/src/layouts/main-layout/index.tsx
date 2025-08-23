import { Outlet } from 'react-router-dom';
import '../../components/base/ATBTheme.css';
import React from 'react';

type Props = { children?: React.ReactNode };

export default function MainLayout({ children }: Props) {
  return (
    <div className="atb-app-bg">
      {/* ATB-style red ribbon */}
      <header className="atb-ribbon">
        <div className="container-fluid d-flex align-items-center justify-content-between py-2 px-3">
          <strong>ATB</strong>
          <nav className="d-none d-md-flex gap-3 small">
            <a className="text-white text-decoration-none opacity-75" href="#">DEMO ATB NET</a>
            <a className="text-white text-decoration-none opacity-75" href="#">DEVENIR CLIENT</a>
            <a className="text-white text-decoration-none opacity-75" href="#">SERVICES</a>
          </nav>
        </div>
      </header>

      <main className="container-fluid py-3">
        <div className="atb-surface p-3">
          {/* Works with both router styles */}
          {children ?? <Outlet />}
        </div>
      </main>
    </div>
  );
}
