import React, { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import MasterLayout from './MasterLayout';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';



const MCQGrading = () => {
  const [questionImage, setQuestionImage] = useState(null);
  const [questionPreview, setQuestionPreview] = useState(null);
  const [answerPdf, setAnswerPdf] = useState(null);
  const [pdfPages, setPdfPages] = useState([]);
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const [answerKey, setAnswerKey] = useState('');
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleQuestionImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setQuestionImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setQuestionPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnswerPdfChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setAnswerPdf(file);
      handlePdfUpload(e);
    }
  };

  const handlePdfUpload = async (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("file", file);
  
    const response = await fetch("http://localhost:5001/convert_pdf", {
      method: "POST",
      body: formData,
    });
  
    const data = await response.json();
    setPdfPages(data.images);
    setCurrentPageIndex(0);
  };
  const handleAnswerKeyChange = (e) => {
    const cleanedInput = e.target.value.replace(/\s/g, '').toUpperCase();
    setAnswerKey(cleanedInput);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!questionImage || !answerPdf || !answerKey.trim()) {
      setError("Please upload both question image and answer PDF, and provide the answer key.");
      return;
    }

    setLoading(true);
    setError(null);
    setScore(null);

    try {
      const formData = new FormData();
      formData.append('questionImage', questionImage);
      formData.append('answerPdf', answerPdf);
      formData.append('answerKey', answerKey);

      const response = await fetch('http://127.0.0.1:5001/mcq', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to grade MCQ');
      }

      const data = await response.json();
      setScore(data.Detected);
    } catch (err) {
      console.error('Error grading MCQ:', err);
      setError('Error grading MCQ. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  const downloadExcel = () => {
    const data = Object.entries(score).map(([studentno, score]) => ({
      studentno,
      score,
    }));
  
    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Scores');
  
    const excelBuffer = XLSX.write(workbook, {
      bookType: 'xlsx',
      type: 'array',
    });
  
    const file = new Blob([excelBuffer], {
      type:
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8',
    });
  
    saveAs(file, 'MCQ_Scores.xlsx');
  };

  return (
    <MasterLayout>
      <div className="max-w-6xl mx-auto p-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">MCQ Grading</h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="flex gap-10 justify-center flex-wrap">
              {/* Question Image Upload */}
              <div className="w-full md:w-5/12">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Question Sheet Image
                </label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleQuestionImageChange}
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-md file:border-0
                    file:text-sm file:font-semibold
                    file:bg-blue-50 file:text-blue-700
                    hover:file:bg-blue-100"
                />
                {questionPreview && (
                  <div className="mt-2">
                    <img
                      src={questionPreview}
                      alt="Question Preview"
                      className="max-w-full h-auto rounded-lg border"
                    />
                  </div>
                )}
              </div>

              {/* Answer PDF Upload */}
              <div className="w-full md:w-5/12">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Answer Sheet PDF
                </label>
                <input
                  type="file"
                  accept="application/pdf"
                  onChange={handleAnswerPdfChange}
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-md file:border-0
                    file:text-sm file:font-semibold
                    file:bg-blue-50 file:text-blue-700
                    hover:file:bg-blue-100"
                />
                          {/* PDF Page Image Preview with Navigation */}
          {pdfPages.length > 0 && (
  <div className="mt-4">
    <img
      src={`http://localhost:5001${pdfPages[currentPageIndex]}`}
      alt={`Page ${currentPageIndex + 1}`}
      className="max-w-full rounded-lg border"
    />

    <div className="flex justify-between mt-4">
      <button
        onClick={() => setCurrentPageIndex((i) => Math.max(i - 1, 0))}
        disabled={currentPageIndex === 0}
        className="text-blue-600 hover:underline disabled:text-gray-400"
      >
        ← Previous
      </button>
      <p>
        Page {currentPageIndex + 1} of {pdfPages.length}
      </p>
      <button
        onClick={() =>
          setCurrentPageIndex((i) => Math.min(i + 1, pdfPages.length - 1))
        }
        disabled={currentPageIndex === pdfPages.length - 1}
        className="text-blue-600 hover:underline disabled:text-gray-400"
      >
        Next →
      </button>
    </div>
  </div>
)}
              </div>
              
            </div>

            {/* Answer Key Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Answer Key
              </label>
              <textarea
                value={answerKey}
                onChange={handleAnswerKeyChange}
                placeholder="Enter answer key (e.g., ABCDABCD)"
                rows={4}
                className="shadow-sm block w-full focus:ring-blue-500 focus:border-blue-500 sm:text-sm border border-gray-300 rounded-md p-2"
              />
              <p className="mt-1 text-sm text-gray-500">
                Enter the correct answers in sequence. Spaces will be removed automatically.
              </p>
            </div>

            {/* Submit Button */}
            <div>
              <button
                type="submit"
                disabled={loading}
                className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white 
                  ${loading
                    ? 'bg-blue-300 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700'
                  }`}
              >
                {loading ? 'Grading...' : 'Grade MCQ'}
              </button>
            </div>
          </form>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-600">
              {error}
            </div>
          )}



          {/* Result Display */}
          {score !== null && !error && (
            <div className="mt-6 p-6 bg-green-50 border border-green-200 rounded-lg">
              <h3 className="text-lg font-medium text-green-900">Results</h3>
              <p className="mt-2 text-xl font-bold text-green-700">
              <div className="space-y-2">
            {Object.entries(score).map(([question, mark]) => (
              <div key={question} className="text-gray-800">
                Student {question}: {mark} marks
              </div>
            ))}
          </div>
              </p>
              <button
  onClick={downloadExcel}
  className="mt-4 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded shadow"
>
  Download Score Sheet
</button>

            </div>
          )}
        </div>
      </div>
    </MasterLayout>
  );
};

export default MCQGrading;
