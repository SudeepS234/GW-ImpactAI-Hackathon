import { motion } from 'framer-motion';
import { Upload, Brain, NotebookPen, MessageSquare, PlayCircle } from 'lucide-react';
import { useNavigate } from "react-router-dom";

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
};

function Home() {
  const navigate = useNavigate();

  const startButton = () => {
    navigate("/upload");
  };
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <motion.section 
        initial="hidden"
        animate="visible"
        variants={fadeIn}
        className="pt-20 pb-16 text-center px-4"
      >
        <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">
          Transform Your Learning Experience
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
          Upload any document or video and let AI help you learn faster and smarter
        </p>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="bg-primary-500 text-white px-8 py-3 rounded-full text-lg font-semibold hover:bg-primary-600 transition-colors"
          onClick={startButton}
        >
          Get Started
        </motion.button>
      </motion.section>

      {/* Features Section */}
      <motion.section 
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        transition={{ staggerChildren: 0.2 }}
        className="py-16 bg-white dark:bg-gray-800"
      >
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900 dark:text-white">
            Features
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                variants={fadeIn}
                className="p-6 rounded-xl bg-gray-50 dark:bg-gray-700 shadow-lg"
              >
                <feature.icon className="w-12 h-12 text-primary-500 mb-4" />
                <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* How it Works Section */}
      <motion.section
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        transition={{ staggerChildren: 0.3 }}
        className="py-16"
      >
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900 dark:text-white">
            How It Works
          </h2>
          <div className="flex flex-col md:flex-row justify-between items-center gap-8">
            {steps.map((step, index) => (
              <motion.div
                key={index}
                variants={fadeIn}
                className="flex flex-col items-center text-center"
              >
                <div className="w-20 h-20 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center mb-4">
                  <step.icon className="w-10 h-10 text-primary-500" />
                </div>
                <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">
                  {step.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  {step.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Product</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-600 dark:text-gray-300 hover:text-primary-500">Features</a></li>
                <li><a href="#" className="text-gray-600 dark:text-gray-300 hover:text-primary-500">Pricing</a></li>
                <li><a href="#" className="text-gray-600 dark:text-gray-300 hover:text-primary-500">Tutorial</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Company</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-600 dark:text-gray-300 hover:text-primary-500">About</a></li>
                <li><a href="#" className="text-gray-600 dark:text-gray-300 hover:text-primary-500">Blog</a></li>
                <li><a href="#" className="text-gray-600 dark:text-gray-300 hover:text-primary-500">Careers</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Resources</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-600 dark:text-gray-300 hover:text-primary-500">Documentation</a></li>
                <li><a href="#" className="text-gray-600 dark:text-gray-300 hover:text-primary-500">Help Center</a></li>
                <li><a href="#" className="text-gray-600 dark:text-gray-300 hover:text-primary-500">Community</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Legal</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-600 dark:text-gray-300 hover:text-primary-500">Privacy</a></li>
                <li><a href="#" className="text-gray-600 dark:text-gray-300 hover:text-primary-500">Terms</a></li>
                <li><a href="#" className="text-gray-600 dark:text-gray-300 hover:text-primary-500">Security</a></li>
              </ul>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

const features = [
  {
    icon: Brain,
    title: 'AI-Powered Summaries',
    description: 'Get instant, comprehensive summaries of your documents'
  },
  {
    icon: NotebookPen,
    title: 'Smart Flashcards',
    description: 'Generate and study with AI-created flashcards'
  },
  {
    icon: MessageSquare,
    title: 'Interactive Chat',
    description: 'Ask questions and get instant answers about your content'
  }
];

const steps = [
  {
    icon: Upload,
    title: 'Upload',
    description: 'Upload any document or video'
  },
  {
    icon: Brain,
    title: 'Generate',
    description: 'AI processes and creates learning materials'
  },
  {
    icon: PlayCircle,
    title: 'Learn',
    description: 'Study with various interactive tools'
  }
];

export default Home;