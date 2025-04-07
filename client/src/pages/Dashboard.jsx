import { motion } from 'framer-motion';
import { FileText, Settings, TrendingUp, Upload } from 'lucide-react';
import { Link } from 'react-router-dom';

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
};

function Dashboard() {
  return (
    <div className="flex min-h-screen pt-16">
      {/* Sidebar */}
      <motion.aside
        initial={{ x: -50, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-4 hidden md:block"
      >
        <div className="space-y-4">
          <div className="flex items-center space-x-3 p-3 rounded-lg bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300">
            <FileText className="w-5 h-5" />
            <span>My Uploads</span>
          </div>
          <div className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
            <TrendingUp className="w-5 h-5" />
            <span>Progress</span>
          </div>
          <div className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
            <Settings className="w-5 h-5" />
            <span>Settings</span>
          </div>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 p-6">
        {/* Stats Section */}
        <motion.div
          initial="hidden"
          animate="visible"
          variants={fadeIn}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm">
            <h3 className="text-lg font-semibold mb-2">XP Points</h3>
            <p className="text-3xl font-bold text-primary-500">1,234</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm">
            <h3 className="text-lg font-semibold mb-2">Current Streak</h3>
            <p className="text-3xl font-bold text-primary-500">7 days ❤️❤️❤️</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm">
            <h3 className="text-lg font-semibold mb-2">Documents</h3>
            <p className="text-3xl font-bold text-primary-500">12</p>
          </div>
        </motion.div>

        {/* Documents List */}
        <motion.div
          initial="hidden"
          animate="visible"
          variants={fadeIn}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6"
        >
          <h2 className="text-2xl font-bold mb-6">Recent Documents</h2>
          <div className="space-y-4">
            {documents.map((doc, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <div className="flex items-center space-x-4">
                  <FileText className="w-6 h-6 text-primary-500" />
                  <div>
                    <h3 className="font-semibold">{doc.title}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Last opened: {doc.lastOpened}</p>
                  </div>
                </div>
                <Link
                  to={`/document/${doc.id}`}
                  className="px-4 py-2 bg-primary-500 text-white rounded-full hover:bg-primary-600 transition-colors"
                >
                  Resume
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </main>

      {/* Floating Action Button */}
      <Link to="/upload">
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="fixed bottom-8 right-8 w-14 h-14 bg-primary-500 text-white rounded-full shadow-lg flex items-center justify-center"
        >
          <Upload className="w-6 h-6" />
        </motion.button>
      </Link>
    </div>
  );
}

const documents = [
  { id: 1, title: 'Machine Learning Basics', lastOpened: '2 hours ago' },
  { id: 2, title: 'React Design Patterns', lastOpened: '1 day ago' },
  { id: 3, title: 'JavaScript ES6 Features', lastOpened: '3 days ago' },
];

export default Dashboard;