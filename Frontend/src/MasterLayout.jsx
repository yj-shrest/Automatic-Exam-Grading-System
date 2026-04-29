import React, { useState } from 'react';
import { User, LogIn, Book, FileText, Menu } from 'lucide-react';
import { Link } from 'react-router-dom';

const MasterLayout = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 justify-between items-center">
            <div className="flex items-center">
              <button
                onClick={() => {
                    console.log("clicked");setIsSidebarOpen(!isSidebarOpen)}}
                className="p-2 rounded-md hover:bg-gray-100"
              >
                <Menu className="h-6 w-6 text-gray-500" />
              </button>
              <Link className="ml-4 text-xl font-semibold text-gray-900" to="/">
                Automatic Exam Grading System
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/login"
                className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md"
              >
                <LogIn className="h-4 w-4 mr-2" />
                Login
              </Link>
              <Link
                to="/signup"
                className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
              >
                <User className="h-4 w-4 mr-2" />
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Sidebar */}
      <div className='flex flex-row'>
        
      <aside
        className={`${
          isSidebarOpen ? 'translate-x-0' : 'translate-x-[-20rem]'
        } transform fixed lg:relative lg:translate-x-0 z-40 w-64 h-screen bg-white border-r transition-transform duration-200 ease-in-out`}
      >
        <nav className="mt-5 px-2">
          <div className="space-y-1">
            <Link
              to="/mcq"
              className="group flex items-center px-2 py-2 text-base font-medium rounded-md text-gray-900 bg-gray-100"
            >
              <Book className="mr-3 h-6 w-6 text-gray-500" />
              MCQ Questions
            </Link>
            <Link
              to="/addDB"
              className="group flex items-center px-2 py-2 text-base font-medium rounded-md text-gray-600 hover:bg-gray-100"
            >
              <FileText className="mr-3 h-6 w-6 text-gray-500" />
              Subjective Questions
            </Link>
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      {children}
      </div>
    </div>
  );
};

export default MasterLayout;