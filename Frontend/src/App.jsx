import { useState } from 'react'
import Home from './Home'
import Mcq from './Mcq';
import SubjectiveGrading from './SubjectiveGrading';
import AddDB from './AddDB';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { LoginForm } from './Login';
import {SignupForm} from './SignUp';
function App() {
  return (
    <Router>
      <Routes>
        <Route path='/' element={<Home/>} />
        <Route path='/mcq'element={<Mcq/>}/>
        <Route path='/subjective'element={<SubjectiveGrading/>}/>
        <Route path='/addDB'element={<AddDB/>}/>
        <Route path='/login'element={<LoginForm/>}/>
        <Route path='/signup'element={<SignupForm/>}/>
      </Routes>
    </Router>
    
  )
}

export default App
