import { Link } from "react-router-dom";

export const LoginForm = () => (
    <div className="bg-gray-100 w-screen h-screen flex flex-col gap-20 items-center justify-center">

        <Link className="ml-4 text-5xl font-semibold text-gray-900" to="/">
                        Automatic Exam Grading System
                      </Link>
    <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Login</h2>
      <form className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-gray-700 mb-2">Email</label>
          <input 
            id="email"
            type="email" 
            className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your email"
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-gray-700 mb-2">Password</label>
          <input 
            id="password"
            type="password" 
            className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your password"
          />
        </div>
        <button 
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700"
        >
          Login
        </button>
        <p className="text-center mt-4">
          Don't have an account? 
          <Link 
            type="button"
            to= "/signup"
            className="text-blue-600 ml-2 hover:underline"
          >
            Sign Up
          </Link>
        </p>
      </form>
    </div>
    </div>
  );