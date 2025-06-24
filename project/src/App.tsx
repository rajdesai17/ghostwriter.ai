import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ToastProvider } from './contexts/ToastContext';
import { MainLayout } from './layouts/MainLayout';
import { Landing } from './pages/Landing';
import { Home } from './pages/Home';
import { Profiles } from './pages/Profiles';
import NavbarDemo from './pages/NavbarDemo';

function App() {
  return (
    <ToastProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/navbar-demo" element={<NavbarDemo />} />
          <Route path="/generate" element={<MainLayout />}>
            <Route index element={<Home />} />
          </Route>
          <Route path="/profiles" element={<MainLayout />}>
            <Route index element={<Profiles />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ToastProvider>
  );
}

export default App;