import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function UploadFicheiros() {
  const [docente, setDocente] = useState(null);
  const [cadeiraSelecionada, setCadeiraSelecionada] = useState('');
  const [ficheiro, setFicheiro] = useState(null);
  const [mensagemStatus, setMensagemStatus] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('docenteLogado'));
    if (!user) {
      navigate('/');
    } else {
      setDocente(user);
    }
  }, [navigate]);

  const handleUpload = async () => {
    if (!cadeiraSelecionada || !ficheiro) {
      mostrarMensagem('⚠️ Preenche todos os campos!', 'erro');
      return;
    }

    const formData = new FormData();
    formData.append('file', ficheiro);
    formData.append('cadeira', cadeiraSelecionada);

    try {
      const response = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData
      });

      const contentType = response.headers.get("content-type");
      const data = contentType && contentType.includes("application/json") ? await response.json() : {};

      if (!response.ok) {
        mostrarMensagem(`❌ Erro ao enviar: ${data.erro || 'Erro inesperado.'}`, 'erro');
        return;
      }

      // Atualiza o localStorage
      const ficheirosPorCadeira = JSON.parse(localStorage.getItem('ficheirosPorCadeira')) || {};
      ficheirosPorCadeira[cadeiraSelecionada] = ficheirosPorCadeira[cadeiraSelecionada] || [];
      ficheirosPorCadeira[cadeiraSelecionada].push(ficheiro.name);
      localStorage.setItem('ficheirosPorCadeira', JSON.stringify(ficheirosPorCadeira));

      mostrarMensagem(`✅ ${data.mensagem}`, 'sucesso');
      setFicheiro(null);
    } catch (error) {
      console.error('Erro ao enviar ficheiro:', error);
      mostrarMensagem('❌ Erro ao enviar o ficheiro!', 'erro');
    }
  };

  const mostrarMensagem = (mensagem, tipo) => {
    setMensagemStatus({ texto: mensagem, tipo });
    setTimeout(() => setMensagemStatus(null), 5000);
  };

  if (!docente) return null;

  return (
    <div style={{ padding: '40px 60px', fontFamily: 'Arial' }}>
      <h2 style={{ fontSize: '28px', marginBottom: '30px' }}>📤 Upload de Ficheiros</h2>

      {mensagemStatus && (
        <div style={{
          marginBottom: 20,
          padding: 15,
          backgroundColor: mensagemStatus.tipo === 'sucesso' ? '#d4edda' : '#f8d7da',
          color: mensagemStatus.tipo === 'sucesso' ? '#155724' : '#721c24',
          border: `1px solid ${mensagemStatus.tipo === 'sucesso' ? '#c3e6cb' : '#f5c6cb'}`,
          borderRadius: 5
        }}>
          {mensagemStatus.texto}
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <div style={{
          background: '#e0e0e0',
          padding: '40px',
          borderRadius: '12px',
          width: '700px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
        }}>
          <p style={{ marginBottom: 20 }}><strong>Docente:</strong> {docente.nome}</p>

          <div style={{ marginBottom: 25 }}>
            <label style={{ display: 'block', marginBottom: 8 }}>Selecionar Cadeira:</label>
            <select
              value={cadeiraSelecionada}
              onChange={(e) => setCadeiraSelecionada(e.target.value)}
              style={{
                padding: 10,
                width: '100%',
                borderRadius: 6,
                border: '1px solid #ccc',
                fontSize: '16px'
              }}
            >
              <option value="">-- Escolhe uma cadeira --</option>
              {docente.cadeiras.map((c, idx) => (
                <option key={idx} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: 25 }}>
            <label style={{ display: 'block', marginBottom: 8 }}>Selecionar Ficheiro:</label>
            <input
              type="file"
              onChange={(e) => setFicheiro(e.target.files[0])}
              style={{ fontSize: '15px' }}
            />
          </div>

          <div style={{ textAlign: 'center' }}>
            <button
              onClick={handleUpload}
              style={{
                background: 'royalblue',
                color: 'white',
                padding: '12px 28px',
                border: 'none',
                borderRadius: 6,
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              Enviar Ficheiros
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UploadFicheiros;
