import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function DashBoardEstudante() {
  const [aluno, setAluno] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const alunoLogado = JSON.parse(localStorage.getItem('alunoLogado'));
    if (!alunoLogado) {
      navigate('/');
    } else {
      setAluno(alunoLogado);
    }
  }, [navigate]);

  const entrarNoChat = (cadeira) => {
    localStorage.setItem('cadeiraSelecionada', cadeira);
    navigate('/chat');
  };

  if (!aluno) return null;

  return (
    <div style={{ padding: '40px', fontFamily: 'Arial' }}>
      <h2 style={{ marginBottom: '30px' }}>🎓 Dashboard do Estudante</h2>

      <div style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '40px',
        marginTop: '40px'
      }}>
        {/* CONTAINER ESQUERDO */}
        <div style={{
          backgroundColor:  '#e0e0e0',
          padding: '30px',
          borderRadius: '12px',
          boxShadow: '0 4px 10px rgba(0,0,0,0.1)',
          width: '300px'
        }}>
          <p><strong>👤 Nome:</strong> {aluno.nome}</p>
          <p><strong>🎓 Curso:</strong> {aluno.curso}</p>
        </div>

        <div style={{
          backgroundColor: '#e0e0e0',
          padding: '30px',
          borderRadius: '12px',
          boxShadow: '0 4px 10px rgba(0,0,0,0.1)',
          width: '400px',
          textAlign: 'center',
          maxHeight: '500px',
          overflowY: 'auto'  // Adiciona isto para scroll
        }}>

          <h4>📄 Cadeiras Disponíveis</h4>
          {aluno.cadeiras.map((cadeira, idx) => (
            <div key={idx} style={{
              backgroundColor:  '#e0e0e0',
              marginTop: '15px',
              padding: '15px',
              borderRadius: '8px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              boxShadow: '0 2px 6px rgba(0,0,0,0.05)'
            }}>
              <span style={{ marginBottom: '10px' }}>{cadeira}</span>
              <button
                onClick={() => entrarNoChat(cadeira)}
                style={{
                  backgroundColor: 'royalblue',
                  color: 'white',
                  padding: '8px 14px',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                Abrir Chatbot
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default DashBoardEstudante;
