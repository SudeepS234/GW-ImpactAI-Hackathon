import { useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

function Summary() {
  const location = useLocation();
  const navigate = useNavigate();
  const { summary, fileName, audioUrl, flashcards, selectedOptions } = location.state || {};


  const audioRef = useRef(null);
  console.log("AUDIO URL:", audioUrl);


  useEffect(() => {
    if (audioRef.current && audioUrl) {
      audioRef.current.load(); // ensure it resets before playing
      audioRef.current.play().catch((err) => {
        console.warn("Autoplay blocked:", err.message);
      });
    }
  }, [audioUrl]);

  if (!summary) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl">⚠️ No summary found.</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 bg-primary-500 text-white px-4 py-2 rounded"
          >
            Back to Upload
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-16 px-6 max-w-5xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-8"
      >
        <h2 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">
          Summary of: {fileName}
        </h2>

        <div className="max-h-[70vh] overflow-y-auto border rounded-md p-4 bg-gray-50 dark:bg-gray-700">
          <p className="whitespace-pre-wrap text-gray-800 dark:text-gray-200 text-lg">
            {summary}
          </p>
        </div>

        {audioUrl && (
          <div className="mt-6">
            <h2 className="text-lg font-semibold mb-2">Listen to Summary</h2>
            <audio controls autoPlay className="w-full">
              <source src={`http://localhost:5000${audioUrl}`} type="audio/mpeg" />
              Your browser does not support the audio element.
            </audio>
          </div>
        )}

        {selectedOptions?.flashcards && flashcards?.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold mb-4">Flashcards</h2>
            <div className="grid gap-4 sm:grid-cols-2">
              {flashcards.map((card, index) => (
                <div
                  key={index}
                  className="bg-yellow-50 dark:bg-gray-900 p-4 rounded-lg shadow-md border border-yellow-200 dark:border-gray-700"
                >
                  <p className="font-semibold text-gray-800 dark:text-white">Q: {card.question}</p>
                  <p className="mt-2 text-gray-600 dark:text-gray-300">A: {card.answer}</p>
                </div>
              ))}
            </div>
          </div>
        )}


        <button
          onClick={() => navigate('/upload')}
          className="mt-6 bg-primary-500 text-white px-4 py-2 rounded hover:bg-primary-600"
        >
          Upload Another
        </button>
      </motion.div>
    </div>
  );
}

export default Summary;
