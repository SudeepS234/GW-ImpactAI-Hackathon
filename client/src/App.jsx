import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import { useState } from 'react';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Summary from './pages/Summary';
import VoiceAssistant from './components/VoiceAssistant';

const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0ea5e9',
    },
  },
});

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#38bdf8',
    },
  },
});

function AppWrapper() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  return (
    <ThemeProvider theme={isDarkMode ? darkTheme : lightTheme}>
      <div className={isDarkMode ? 'dark' : ''}>
        <Router>
          <AppRoutes isDarkMode={isDarkMode} setIsDarkMode={setIsDarkMode} />
        </Router>
      </div>
    </ThemeProvider>
  );
}

function AppRoutes({ isDarkMode, setIsDarkMode }) {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <Navbar isDarkMode={isDarkMode} setIsDarkMode={setIsDarkMode} />

      {/* Voice Assistant active globally */}
      <VoiceAssistant />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/Summary" element={<Summary />} />
      </Routes>
    </div>
  );
}

export default AppWrapper;