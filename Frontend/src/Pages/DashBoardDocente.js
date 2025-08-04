import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function DashBoardDocente() {
  const [docente, setDocente] = useState(null);
  const [ficheirosPorCadeira, setFicheirosPorCadeira] = useState({});
  const [cadeiraAtiva, setCadeiraAtiva] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('docenteLogado'));
    if (user) {
      setDocente(user);
      const ficheiros = JSON.parse(localStorage.getItem('ficheirosPorCadeira')) || {};
      setFicheirosPorCadeira(ficheiros);
    } else {
      navigate('/');
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('docenteLogado');
    navigate('/');
  };

  const handleIrParaUpload = () => {
    navigate('/upload');
  };

  const removerFicheiro = (ficheiro) => {
    const copia = { ...ficheirosPorCadeira };
    if (copia[cadeiraAtiva]) {
      copia[cadeiraAtiva] = copia[cadeiraAtiva].filter(f => f !== ficheiro);
      localStorage.setItem('ficheirosPorCadeira', JSON.stringify(copia));
      setFicheirosPorCadeira(copia);
    }
  };

  if (!docente) return null;

  return (
    <div style={{ padding: '40px 60px' }}>
      <h2 style={{ fontSize: '28px', marginBottom: '30px' }}>📚 Dashboard do Docente</h2>

      <div style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '40px',
        marginTop: '40px'
      }}>
        {/* Painel Esquerdo */}
        <div style={{
          background: '#e0e0e0',
          padding: '30px',
          borderRadius: '12px',
          width: '400px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
        }}>
          <p><strong>Bem-vindo(a),</strong> {docente.nome}</p>

          <h4>Cadeiras lecionadas:</h4>
          <ul style={{ listStyleType: 'disc', paddingLeft: '20px' }}>
            {docente.cadeiras.map((c, idx) => (
              <li
                key={idx}
                style={{
                  cursor: 'pointer',
                  color: cadeiraAtiva === c ? 'blue' : 'black',
                  fontWeight: cadeiraAtiva === c ? 'bold' : 'normal',
                  marginBottom: '6px'
                }}
                onClick={() => setCadeiraAtiva(c)}
              >
                {c}
              </li>
            ))}
          </ul>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '40px' }}>
            <button
              style={{
                padding: '10px 20px',
                fontSize: '16px',
                borderRadius: '6px',
                border: '1px solid #ccc',
                cursor: 'pointer'
              }}
              onClick={handleIrParaUpload}
            >
              Upload
            </button>
            <button
              style={{
                padding: '10px 20px',
                fontSize: '16px',
                borderRadius: '6px',
                border: '1px solid #ccc',
                cursor: 'pointer'
              }}
              onClick={handleLogout}
            >
              Sair
            </button>
          </div>
        </div>

        {/* Painel Direito */}
        <div style={{
          background: '#e0e0e0',
          padding: '30px',
          borderRadius: '12px',
          width: '400px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
        }}>
          <h4>📁 Ficheiros enviados {cadeiraAtiva ? `em "${cadeiraAtiva}"` : ''}</h4>
          {cadeiraAtiva && ficheirosPorCadeira[cadeiraAtiva] ? (
            <ul style={{ paddingLeft: '0px' }}>
              {ficheirosPorCadeira[cadeiraAtiva].map((f, i) => (
                <li
                  key={i}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '6px 0',
                    listStyleType: 'none'
                  }}
                >
                  <span>{f}</span>
                  <button
                    onClick={() => removerFicheiro(f)}
                    style={{
                      backgroundColor: 'crimson',
                      color: 'white',
                      border: 'none',
                      borderRadius: 4,
                      padding: '4px 8px',
                      cursor: 'pointer'
                    }}
                  >
                    🗑️
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p>Seleciona uma cadeira para ver os ficheiros.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default DashBoardDocente;
