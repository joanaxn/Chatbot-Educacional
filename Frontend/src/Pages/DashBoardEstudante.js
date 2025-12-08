import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function DashboardEstudante() {
  const [aluno, setAluno] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const a = JSON.parse(localStorage.getItem('alunoLogado'));
    if (!a) {
      navigate('/'); // volta ao login se não houver sessão
      return;
    }
    setAluno(a);
  }, [navigate]);

  const abrirChat = (cadeira) => {
    // grava a cadeira escolhida no localStorage
    localStorage.setItem('cadeiraSelecionada', cadeira);
    // navega para o chat com a cadeira certa
    navigate(`/chat?cadeira=${encodeURIComponent(cadeira)}`);
  };

  if (!aluno) return null;

  return (
    <div style={{ padding: '40px 60px' }}>
      <h2 style={{ fontSize: '28px', marginBottom: '30px' }}>🎓 Dashboard do Estudante</h2>

      <div style={{ display: 'flex', gap: '40px', alignItems: 'flex-start' }}>
        {/* Painel esquerdo: info + cadeiras inscritas */}
        <div style={{
          background: '#e0e0e0',
          padding: '30px',
          borderRadius: '12px',
          width: '520px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
        }}>
          <p><strong>👤 Nome:</strong> {aluno.nome}</p>

          <div style={{ marginTop: 16 }}>
            <p style={{ marginBottom: 8, fontWeight: 'bold' }}>📚 Cadeiras inscritas:</p>
            {aluno.cadeiras?.length ? (
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {aluno.cadeiras.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            ) : (
              <p style={{ color: '#666', fontStyle: 'italic' }}>Sem inscrições.</p>
            )}
          </div>
        </div>

        {/* Painel direito: ações por cadeira */}
        <div style={{
          background: '#e0e0e0',
          padding: '30px',
          borderRadius: '12px',
          minWidth: '520px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
        }}>
          <p style={{ marginBottom: 16, fontWeight: 'bold' }}>🧠 Cadeiras disponíveis</p>

          {aluno.cadeiras?.length ? (
            aluno.cadeiras.map((c, i) => (
              <div key={i} style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                background: '#f4f4f4',
                borderRadius: 8,
                padding: '14px 16px',
                marginBottom: 12
              }}>
                <span>{c}</span>
                <button
                  onClick={() => abrirChat(c)}
                  style={{
                    background: 'royalblue',
                    color: 'white',
                    padding: '8px 14px',
                    border: 'none',
                    borderRadius: 6,
                    cursor: 'pointer'
                  }}
                >
                  Abrir Chatbot
                </button>
              </div>
            ))
          ) : (
            <p style={{ color: '#666', fontStyle: 'italic' }}>Sem cadeiras para abrir.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default DashboardEstudante;
 