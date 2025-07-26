import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [tipo, setTipo] = useState('estudante');
  const [erro, setErro] = useState('');
  const navigate = useNavigate();

  const handleLogin = () => {
    const dados = JSON.parse(localStorage.getItem(tipo === 'docente' ? 'professores' : 'alunos')) || [];
    const user = dados.find(u => u.email === email && u.password === password);

    if (user) {
      setErro('');
      if (tipo === 'docente') {
        localStorage.setItem('docenteLogado', JSON.stringify(user));
        navigate('/docente');
      } else {
        localStorage.setItem('alunoLogado', JSON.stringify(user));
        navigate('/estudante');
      }
    } else {
      setErro('Credenciais inválidas. Verifica o email, a password e o tipo.');
    }
  };

  const seedFakeDatabase = () => {
    const professores = [
      { nome: "Ana Silva", email: "ana.silva@upt.pt", password: "ana123", curso: "Engenharia Informática", cadeiras: ["Inteligência Artificial", "Redes"] },
      { nome: "Carlos Mendes", email: "carlos.mendes@upt.pt", password: "carlos123", curso: "Design Multimédia", cadeiras: ["Design Gráfico", "Animação"] },
      { nome: "Maria Costa", email: "maria.costa@upt.pt", password: "maria123", curso: "Gestão", cadeiras: ["Marketing", "Gestão Financeira"] }
    ];

    const alunos = [
      { nome: "João Lopes", email: "joao.lopes@upt.pt", password: "joao123", curso: "Engenharia Informática", cadeiras: ["Redes"] },
      { nome: "Inês Rocha", email: "ines.rocha@upt.pt", password: "ines123", curso: "Design Multimédia", cadeiras: ["Design Gráfico"] },
      { nome: "Tiago Neves", email: "tiago.neves@upt.pt", password: "tiago123", curso: "Gestão", cadeiras: ["Marketing"] }
    ];

    localStorage.setItem("professores", JSON.stringify(professores));
    localStorage.setItem("alunos", JSON.stringify(alunos));
    alert("Base de dados fictícia carregada com sucesso!");
  };

  const seedFicheirosPorCadeira = () => {
    const ficheiros = {
      "Redes": ["Aula1_Redes.pdf", "Topologias_Redes.docx", "Resumo_Redes.pptx"],
      "Inteligência Artificial": ["Intro_IA.pdf", "Redes_Neurais.pptx"],
      "Design Gráfico": ["Teoria_Cores.pdf", "Briefing_Creativo.docx"],
      "Animação": ["Frame_By_Frame.pptx"],
      "Marketing": ["Plano_Marketing.pdf", "Exercicios_Mkt.docx"],
      "Gestão Financeira": ["Relatorio_Contas2024.xlsx"]
    };

    localStorage.setItem("ficheirosPorCadeira", JSON.stringify(ficheiros));
    alert("📁 Ficheiros por cadeira carregados com sucesso!");
  };

  return (
    <div className="login-wrapper">
      <div className="login-box">
        <h2>Login</h2>

        <input type="text" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
        <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />

        <select value={tipo} onChange={e => setTipo(e.target.value)}>
          <option value="estudante">Estudante</option>
          <option value="docente">Docente</option>
        </select>

        <button className="btn-login" onClick={handleLogin}>Entrar</button>

        {erro && <p className="error-msg">{erro}</p>}

        <div style={{ marginTop: 20 }}>
          <button className="btn-docente" onClick={() => navigate('/registo-professor')}>Registar como Docente</button>
          <button className="btn-aluno" onClick={() => navigate('/registo-aluno')}>Registar como Aluno</button>
        </div>

        <button className="btn-db" onClick={seedFakeDatabase}>💾 Carregar Base de Dados Fictícia</button>
        <button className="btn-files" onClick={seedFicheirosPorCadeira}>📁 Carregar Ficheiros Fictícios</button>
      </div>
    </div>
  );
}

export default Login;
