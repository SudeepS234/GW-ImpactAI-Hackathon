import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Upload as UploadIcon,
  FileText,
  Book,
  Brain,
  Music
} from 'lucide-react';

function Upload() {
  const [selectedOptions, setSelectedOptions] = useState({
    summary: true,
    flashcards: false,
    quiz: false,
    audio: false,
  });

  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadedFileName, setUploadedFileName] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const navigate = useNavigate();

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploadedFile(file);
    setUploadedFileName(file.name);
  }, []);

  const handleGenerate = async () => {
    if (!uploadedFile) return;

    setIsUploading(true);

    const formData = new FormData();
    formData.append("file", uploadedFile);
    formData.append("options", JSON.stringify(selectedOptions));

    try {
      const response = await fetch("http://localhost:5000/summary", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log("Response from backend:", data); // Debug log

      if (response.ok) {
        navigate('/summary', {
          state: {
            summary: data.summary,
            fileName: uploadedFile.name,
            selectedOptions,
            audioUrl: data.audio_url || null  // Ensure we send null if undefined
          }
        });
      } else {
        console.error("Error:", data.error);
      }
    } catch (err) {
      console.error("Upload failed", err);
    } finally {
      setIsUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
  });

  const toggleOption = (option) => {
    setSelectedOptions((prev) => ({
      ...prev,
      [option]: !prev[option],
    }));
  };

  return (
    <div className="min-h-screen pt-20 px-4">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-8"
        >
          <h1 className="text-3xl font-bold text-center mb-8">Upload Your Document</h1>

          {/* Dropzone */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors
              ${isDragActive
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                : 'border-gray-300 dark:border-gray-600 hover:border-primary-500 dark:hover:border-primary-500'
              }`}
          >
            <input {...getInputProps()} />
            <UploadIcon className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg mb-2">
              {isDragActive
                ? "Drop your files here"
                : uploadedFileName
                  ? `📄 ${uploadedFileName}`
                  : "Drag & drop your files here"}
            </p>
            {!uploadedFileName && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-primary-500 text-white px-6 py-2 rounded-full hover:bg-primary-600 transition-colors"
              >
                Browse Files
              </motion.button>
            )}
          </div>

          {/* Options */}
          <div className="mt-8 grid grid-cols-2 sm:grid-cols-4 gap-4">
            <OptionToggle
              label="Summary"
              icon={<FileText />}
              active={selectedOptions.summary}
              onClick={() => toggleOption('summary')}
            />
            <OptionToggle
              label="Flashcards"
              icon={<Book />}
              active={selectedOptions.flashcards}
              onClick={() => toggleOption('flashcards')}
            />
            <OptionToggle
              label="Quiz"
              icon={<Brain />}
              active={selectedOptions.quiz}
              onClick={() => toggleOption('quiz')}
            />
            <OptionToggle
              label="Audio"
              icon={<Music />}
              active={selectedOptions.audio}
              onClick={() => toggleOption('audio')}
            />
          </div>

          {/* Generate Button */}
          <div className="mt-8 text-center">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              disabled={isUploading || !uploadedFile || !selectedOptions.summary}
              onClick={handleGenerate}
              className={`px-8 py-3 rounded-full font-semibold text-white transition-all 
                ${isUploading || !uploadedFileName || !selectedOptions.summary
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-primary-500 hover:bg-primary-600'
                }`}
            >
              {isUploading ? 'Generating...' : 'Generate'}
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function OptionToggle({ label, icon, active, onClick }) {
  return (
    <motion.button
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`flex flex-col items-center p-4 rounded-xl border 
        ${active
          ? 'bg-primary-100 text-primary-700 border-primary-300 dark:bg-primary-900/20 dark:text-white'
          : 'bg-gray-100 text-gray-700 border-gray-300 dark:bg-gray-700 dark:text-gray-200'
        } hover:shadow-md transition`}
    >
      {icon}
      <span className="mt-2 text-sm font-medium">{label}</span>
    </motion.button>
  );
}

export default Upload;
