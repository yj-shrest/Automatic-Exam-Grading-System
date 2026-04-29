import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MasterLayout from './MasterLayout';

const AddDB = () => {
  const [databaseOption, setDatabaseOption] = useState('existing');
  const [selectedDatabase, setSelectedDatabase] = useState('');
  const [databaseList, setDatabaseList] = useState(["Artificial Intelligence", "Engineering Economics", "Software Engineering"]);
  const [newDatabaseName, setNewDatabaseName] = useState('');
  const [databaseFile, setDatabaseFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [totalPages, setTotalPages] = useState(0);
  const [progress, setProgress] = useState(0);

  const navigate = useNavigate();
  // Fetch available databases on component mount
  useEffect(() => {
    const fetchDatabases = async () => {
      setLoading(true);
      try {
        const response = await fetch('http://127.0.0.1:5000/all_databases');
        if (!response.ok) {
          throw new Error('Failed to fetch databases');
        }
        const data = await response.json();
        console.log(data.databases[0]);
        setDatabaseList(data.databases[0] || []);
        if (data.databases && data.databases.length > 0) {
          setSelectedDatabase(data.databases[0].id);
        }
      } catch (err) {
        setError('Error loading databases. Please try again.');
        console.error('Error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDatabases();
  }, []);

  const handleDatabaseOptionChange = (e) => {
    setDatabaseOption(e.target.value);
  };

  const handleDatabaseSelection = (e) => {
    setSelectedDatabase(e.target.value);
  };

  const handleDatabaseNameChange = (e) => {
    setNewDatabaseName(e.target.value);
  };

  const handleDatabaseFileChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setDatabaseFile(file);
        const formData = new FormData();
        formData.append('file', file);

        try {
          const response = await fetch('http://127.0.0.1:5000/count', {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            throw new Error('Failed to fetch page count');
          }

          const data = await response.json();
          console.log('Number of pages:', data.num_pages);
            setTotalPages(data.num_pages);
        } catch (err) {
          setError('Error fetching page count. Please try again.');
          console.error('Error:', err);
        }
    }
    
  };

 

  const validateForm = () => {
    if (databaseOption === 'existing' && !selectedDatabase) {
      setError("Please select a reference database");
      return false;
    }

    if (databaseOption === 'new') {
      if (!newDatabaseName.trim()) {
        setError("Please enter a name for the new database");
        return false;
      }
      if (!databaseFile) {
        setError("Please upload a PDF file for the new database");
        return false;
      }
    }

    return true;
  };

  const handleSubmit = async (e) => {
    // navigate('/subjective');
    e.preventDefault();
    if (!validateForm()) return;

    setSubmitting(true);
    setError(null);
    const intervalId = setInterval(() => {
        setProgress((prevProgress) => {
            // Check if progress reached the target
            if (prevProgress >= totalPages - 1) {
                clearInterval(intervalId); // Stop the interval
                return totalPages - 1; // Ensure it doesn't exceed the target
            }
            return prevProgress + 1;
        });
    }, 3000);
    try {
      const formData = new FormData();
      if (databaseOption === 'existing') {
        navigate('/subjective', { state: { databaseId: selectedDatabase } });
      } else {
        formData.append('database_name', newDatabaseName);
        formData.append('file', databaseFile);
        
        const response = await fetch('http://127.0.0.1:5000/add_database', {
            method: 'POST',
            body: formData,
        });
        
        if (!response.ok) {
            throw new Error('Failed to grade subjective answer');
        }
        navigate('/subjective', { state: { databaseId: newDatabaseName } });
    }

    } catch (err) {
      setError('Error grading subjective answer. Please try again.');
      console.error('Error:', err);
    } finally {
      setSubmitting(false);
    }
  };



  return (
    <MasterLayout><div className="max-w-4xl mx-auto p-6">
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Reference Database</h2>
      
      {loading ? (
        <div className="text-center py-4">
          <p>Loading databases...</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Database Selection Section */}
          <div className="bg-gray-50 p-4 rounded-lg">              
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    value="existing"
                    checked={databaseOption === 'existing'}
                    onChange={handleDatabaseOptionChange}
                    className="form-radio h-4 w-4 text-blue-600"
                  />
                  <span className="ml-2">Choose from existing database</span>
                </label>
                
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    value="new"
                    checked={databaseOption === 'new'}
                    onChange={handleDatabaseOptionChange}
                    className="form-radio h-4 w-4 text-blue-600"
                  />
                  <span className="ml-2">Add new database</span>
                </label>
              </div>
              
              {databaseOption === 'existing' && (
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Reference Database
                  </label>
                  <select
                    value={selectedDatabase}
                    defaultValue=""
                    onChange={handleDatabaseSelection}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                  >
                    <option value="" disabled>Select a database</option>
                    {databaseList.length === 0 ? (
                      <option value="">No databases available</option>
                    ) : (
                      databaseList.map(db => (
                        <option className='text-black' key={db.id} value={db.id}>
                          {db}
                        </option>
                      ))
                    )}
                  </select>
                </div>
              )}
              
              {databaseOption === 'new' && (
                <div className="mt-4 space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Database Name
                    </label>
                    <input
                      type="text"
                      value={newDatabaseName}
                      onChange={handleDatabaseNameChange}
                      placeholder="Enter a name for the new database"
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Upload PDF Reference File
                    </label>
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={handleDatabaseFileChange}
                      className="block w-full text-sm text-gray-500
                        file:mr-4 file:py-2 file:px-4
                        file:rounded-md file:border-0
                        file:text-sm file:font-semibold
                        file:bg-blue-50 file:text-blue-700
                        hover:file:bg-blue-100"
                    />
                    <p className="mt-1 text-sm text-gray-500">
                      Upload a PDF file containing reference material (textbook, notes, etc.)
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
          <div>
            <button
              type="submit"
              disabled={submitting}
              className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white 
                ${submitting ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
            >
              {submitting ? 'Adding Database' : 'Next'}
            </button>
          </div>
        </form>
      )}
      {submitting && 
      (
          <div className="w-[100%] bg-gray-200 rounded-full h-10 mt-4">
          <div
          className="bg-blue-600 h-10 rounded-full"
          style={{ width: `${(progress / totalPages) * 100}%` }}
          >
          </div>
          </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Result Display */}
    </div>
  </div></MasterLayout>
    
  );
};

export default AddDB;