import React from 'react';
import Navbar from './components/Navbar';
import './App.css';
import { Routes, Route, useLocation } from 'react-router-dom';
import Login from './Pages/Login';
import DashBoardDocente from './Pages/DashBoardDocente';
import DashBoardEstudante from './Pages/DashBoardEstudante';
import UploadPage from './Pages/UploadPage';
import StudentChatPage from './Pages/StudentChatPage';
import RegisterAluno from './Pages/RegisterAluno';
import RegisterProfessor from './Pages/RegisterProfessor';

function App() {
 // const location = useLocation();
  const mostrarNavbar = true;

  return (
    <>
      {mostrarNavbar && <Navbar />}
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/docente" element={<DashBoardDocente />} />
        <Route path="/estudante" element={<DashBoardEstudante />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/chat" element={<StudentChatPage />} />
        <Route path="/registo-aluno" element={<RegisterAluno />} />
        <Route path="/registo-professor" element={<RegisterProfessor />} />
      </Routes>
    </>
  );
}

export default App;
