import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [tipo, setTipo] = useState('estudante');
  const [erro, setErro] = useState('');
  const navigate = useNavigate();

  const handleLogin = () => {
    const endpoint = tipo === 'docente' ? 'login_docente' : 'login_estudante';

    fetch(`http://localhost:8000/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
      .then(res => res.json())
      .then(data => {
        if (!data.erro) {
          setErro('');
          if (tipo === 'docente') {
            localStorage.setItem('docenteLogado', JSON.stringify(data));
            navigate('/docente');
          } else {
            localStorage.setItem('alunoLogado', JSON.stringify(data));
            navigate('/estudante');
          }
        } else {
          setErro(data.erro);
        }
      })
      .catch(() => setErro('Erro ao ligar ao servidor.'));
  };

  return (
    <div className="login-wrapper">
      <div className="login-box">
        <h2>Login</h2>

        <input
          type="text"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />

        <select value={tipo} onChange={e => setTipo(e.target.value)}>
          <option value="estudante">Estudante</option>
          <option value="docente">Docente</option>
        </select>

        <button className="btn-login" onClick={handleLogin}>Entrar</button>

        {erro && <p className="error-msg">{erro}</p>}

        <div style={{ marginTop: 20 }}>
          <button className="btn-docente" onClick={() => navigate('/registo-professor')}>
            Registar como Docente
          </button>
          <button className="btn-aluno" onClick={() => navigate('/registo-aluno')}>
            Registar como Aluno
          </button>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
