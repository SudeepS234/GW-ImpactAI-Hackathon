import { useEffect, useRef, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import { useSpeechSynthesis } from 'react-speech-kit';

export default function VoiceAssistant() {
  const navigate = useNavigate();
  const location = useLocation();
  const { speak } = useSpeechSynthesis();

  const welcomeCount = useRef(0);
  const [hasWelcomed, setHasWelcomed] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState(null);

  // Speak using selected voice
  const speakWithVoice = (text) => {
    if (selectedVoice) {
      speak({ text, voice: selectedVoice });
    } else {
      console.warn('[VoiceAssistant] No voice selected!');
    }
  };

  // Voice commands
  const commands = [
    {
      command: ['Go to upload', 'Open upload page', 'Upload'],
      callback: () => {
        console.log('[VoiceAssistant] Command matched: Go to upload');
        navigate('/upload');
      }
    },
    {
      command: ['Go to dashboard', 'Open dashboard', 'Dashboard'],
      callback: () => {
        console.log('[VoiceAssistant] Command matched: Go to dashboard');
        navigate('/dashboard');
      }
    },
    {
      command: ['Go home', 'Home page', 'Go to home', 'Go back home'],
      callback: () => {
        console.log('[VoiceAssistant] Command matched: Go home');
        navigate('/');
      }
    }
  ];

  const { browserSupportsSpeechRecognition } = useSpeechRecognition({ commands });

  // Load voices reliably
  useEffect(() => {
    let interval;

    const loadVoices = () => {
      const voicesList = window.speechSynthesis.getVoices();
      if (voicesList.length > 0) {
        const preferred = voicesList.find(v => v.lang.includes('en')) || voicesList[0];
        setSelectedVoice(preferred);
        console.log('[VoiceAssistant] ✅ Voice loaded:', preferred.name);
        clearInterval(interval);
      }
    };

    loadVoices();
    interval = setInterval(loadVoices, 200);
    window.speechSynthesis.onvoiceschanged = loadVoices;

    return () => clearInterval(interval);
  }, []);

  // Speak welcome message once or twice
  useEffect(() => {
    if (!browserSupportsSpeechRecognition || !selectedVoice) return;

    if (welcomeCount.current < 2 && !hasWelcomed) {
      welcomeCount.current += 1;
      setHasWelcomed(true);

      console.log('[VoiceAssistant] Speaking welcome message...');
      speakWithVoice('Welcome! You can say commands like go to upload or open dashboard.');

      const listenDelay = setTimeout(() => {
        console.log('[VoiceAssistant] Listening started after welcome...');
        SpeechRecognition.startListening({ continuous: true });
        setHasWelcomed(false);
      }, 3000);

      return () => clearTimeout(listenDelay);
    } else {
      console.log('[VoiceAssistant] Auto-starting listening...');
      SpeechRecognition.startListening({ continuous: true });
    }

    return () => {
      console.log('[VoiceAssistant] Cleanup: stopping listener...');
      SpeechRecognition.stopListening();
    };
  }, [hasWelcomed, selectedVoice]);

  // Speak current page on location change
  useEffect(() => {
    if (!selectedVoice) return;

    const announcePage = {
      '/': 'You are on the home page',
      '/upload': 'You are on the upload page',
      '/dashboard': 'You are on the dashboard',
    };

    const message = announcePage[location.pathname] ||
      (location.pathname.startsWith('/document') && 'You are on the document page');

    if (message) {
      console.log(`[VoiceAssistant] Page changed to ${location.pathname}. Speaking: ${message}`);
      speakWithVoice(message);
    }
  }, [location.pathname, selectedVoice]);

  return null;
}