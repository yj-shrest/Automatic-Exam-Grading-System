import React from 'react'
import { useState } from 'react'
import { useLocation } from 'react-router-dom';
import MasterLayout from './MasterLayout';
const SubjectiveGrading = () => {
    const location = useLocation();
    const {databaseId} = location.state;
    console.log(databaseId);

    const [question, setQuestion] = useState('');
    const [idealAnswer, setIdealAnswer] = useState('');
    const [fullMarks, setFullMarks] = useState(10);
    const [answerfile, setAnswerfile] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const [result, setResult] = useState(null); 
    const [comment, setComment] = useState(null)

    const handleAnswerImageChange = (e) => {
        const file = e.target.files[0];
        if (file && file.type === "application/pdf") {
            setAnswerfile(file);
        } else {
            alert("Please upload a PDF file.");
        }
    }

    const handleSubmit = async () => {
        // Validate inputs
        if (!question.trim()) {
            alert("Please enter the question.");
            return;
        }
        if (!answerfile) {
            alert("Please upload an answer file.");
            return;
        }

        setSubmitting(true);
        const formData = new FormData();
        
        // Append all inputs to formData
        formData.append("question", question);
        formData.append("ideal_answer",idealAnswer.trim() || '');
        formData.append("full_marks", fullMarks);
        formData.append("answer", answerfile);
        formData.append("database_name", databaseId);

        try {
            const response = await fetch(`http://localhost:5000/subjective`, {
                method: "POST",
                body: formData,
            });
            const data = await response.json();
            console.log(data);
            setResult(data.grade);
            setComment(data.comment)
        } catch (error) {
            console.log(error);
            alert("An error occurred while grading the answer.");
        } finally {
            setSubmitting(false);
        }
    }
    return (
        <MasterLayout>
        <div className="max-w-4xl mx-auto p-6 mt-4">
            <div className='bg-white rounded-lg shadow-lg p-6'>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Subjective Question Grading</h2>
                
                {/* Question Text Input */}
                <label className="block text-sm font-medium text-gray-700 mb-2 mt-2">
                    Question
                </label>
                <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Enter the question here"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    required
                />

                {/* Ideal Answer Input (Optional) */}
                <label className="block text-sm font-medium text-gray-700 mb-2 mt-2">
                    Ideal Answer (Optional)
                </label>
                <textarea
                    value={idealAnswer}
                    onChange={(e) => setIdealAnswer(e.target.value)}
                    placeholder="Enter the ideal answer here (optional)"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                />

                {/* Full Marks Input */}
                <label className="block text-sm font-medium text-gray-700 mb-2 mt-2">
                    Full Marks
                </label>
                <input
                    type="number"
                    value={fullMarks}
                    onChange={(e) => setFullMarks(Number(e.target.value))}
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                {/* Answer File Upload */}
                <label className="block text-sm font-medium text-gray-700 mb-2 mt-2">
                    Upload Answer File
                </label>
                <div className="mt-1 flex flex-col space-y-4">
                    <input
                        type="file"
                        accept=".pdf"
                        onChange={handleAnswerImageChange}
                        className="block w-full text-sm text-gray-500
                            file:mr-4 file:py-2 file:px-4
                            file:rounded-md file:border-0
                            file:text-sm file:font-semibold
                            file:bg-blue-50 file:text-blue-700
                            hover:file:bg-blue-100"
                    />
                </div>

                {/* Submit Button */}
                <button
                    onClick={handleSubmit}                
                    disabled={submitting}
                    className={`w-full flex justify-center py-2 px-4 border mt-4 border-transparent rounded-md shadow-sm text-sm font-medium text-white 
                        ${submitting ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
                >
                    {submitting ? 'Grading...' : 'Grade Subjective Answer'}
                </button>

                {/* Result Display */}
                {result && (
                    <div className="mt-6 p-6 bg-green-50 border border-green-200 rounded-lg">
                        <h3 className="text-lg font-medium text-green-900">Results</h3>
                        <div className="mt-2">
                            <p className="text-xl font-bold text-green-700">
                                {result}
                            </p>
                            <div className="mt-2">
                                <p className='text-md font-semibold text-black'>{comment}</p>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
        </MasterLayout>
    )
}

export default SubjectiveGrading