import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import MasterLayout from './MasterLayout';

const Home = () => {
  // const [isLoginOpen, setIsLoginOpen] = useState(false);
  // const [isSignupOpen, setIsSignupOpen] = useState(false);
  const [activeForm, setActiveForm] = useState('login');

  


  return (
    <MasterLayout className="flex-1 p-6">
      <div className="max-w-7xl mx-auto">
         
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Welcome to Automatic Exam Grading System
            </h2>
            <p className="text-gray-600 mb-6">
              Streamline your grading process with our automated system. Handle both MCQ and Objective questions efficiently.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">MCQ Questions</h3>
                <p className="text-gray-600 mb-4">
                  Grade multiple choice questions automatically with our intelligent system.
                </p>
                <Link 
                  to='/mcq' 
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Start Grading MCQs
                </Link>
              </div>
              
              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Subjective Questions</h3>
                <p className="text-gray-600 mb-4">
                  Evaluate objective-type questions with our advanced grading algorithms.
                </p>
                <Link 
                  to='/addDB' 
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Start Grading Objectives
                </Link>
              </div>
            </div>
          </div>
      </div>
    </MasterLayout>
  );
};



export default  Home;