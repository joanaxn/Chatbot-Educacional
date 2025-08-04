import React, { useEffect, useState } from 'react';

function UploadPage() {
  const [cadeira, setCadeira] = useState('');
  const [listaCadeiras, setListaCadeiras] = useState([]);
  const [ficheiros, setFicheiros] = useState([]);
  const [selecionados, setSelecionados] = useState([]);
  const [mensagem, setMensagem] = useState('');

  useEffect(() => {
    const docente = JSON.parse(localStorage.getItem('docenteLogado'));
    if (docente) {
      fetch(`http://localhost:8000/listar_cadeiras_docente?email=${docente.email}`)
        .then((res) => res.json())
        .then((data) => {
          setListaCadeiras(data.cadeiras || []);
        })
        .catch(() => {
          setMensagem('❌ Erro ao carregar as cadeiras.');
        });
    } else {
      setMensagem('❌ Docente não autenticado.');
    }
  }, []);

  useEffect(() => {
    if (cadeira) {
      fetch(`http://localhost:8000/listar_ficheiros?cadeira=${cadeira}`)
        .then((res) => res.json())
        .then((data) => {
          setFicheiros(data.ficheiros || []);
          setSelecionados([]);
        })
        .catch(() => {
          setMensagem('❌ Erro ao carregar os ficheiros.');
        });
    } else {
      setFicheiros([]);
      setSelecionados([]);
    }
  }, [cadeira]);

  const handleCheckboxChange = (ficheiro) => {
    setSelecionados((prev) =>
      prev.includes(ficheiro)
        ? prev.filter((f) => f !== ficheiro)
        : [...prev, ficheiro]
    );
  };

  const confirmarFicheiros = () => {
    if (!cadeira || selecionados.length === 0) {
      setMensagem('⚠️ Seleciona uma cadeira e pelo menos um ficheiro.');
      return;
    }

    fetch('http://localhost:8000/confirmar_ficheiros', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cadeira: cadeira, ficheiros: selecionados }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.mensagem === "novos") {
          setMensagem('✅ Ficheiros confirmados com sucesso!');
        } else {
          setMensagem('⚠️ Estes ficheiros já tinham sido enviados antes.');
        }
      })
      .catch(() => {
        setMensagem('❌ Erro ao confirmar ficheiros.');
      });
  };

  return (
    <div style={{ padding: '40px 60px', fontFamily: 'Arial' }}>
      <h2 style={{ fontSize: '28px', marginBottom: '30px' }}>📁 Confirmar Documentos</h2>

      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <div style={{
          background: '#e0e0e0',
          padding: '40px',
          borderRadius: '12px',
          width: '700px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ marginBottom: 25 }}>
            <label style={{ display: 'block', marginBottom: 8 }}>Selecionar Cadeira:</label>
            <select
              value={cadeira}
              onChange={(e) => setCadeira(e.target.value)}
              style={{
                padding: 10,
                width: '100%',
                borderRadius: 6,
                border: '1px solid #ccc',
                fontSize: '16px'
              }}
            >
              <option value="">-- Escolhe uma cadeira --</option>
              {listaCadeiras.map((c, idx) => (
                <option key={idx} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {cadeira && (
            <>
              <h3 style={{ marginBottom: 15 }}>Ficheiros disponíveis para <em>{cadeira}</em>:</h3>

              {ficheiros.length === 0 ? (
                <p style={{ color: '#888', fontStyle: 'italic' }}>Nenhum ficheiro disponível.</p>
              ) : (
                <ul style={{ listStyle: 'none', padding: 0, marginBottom: 20 }}>
                  {ficheiros.map((ficheiro, index) => (
                    <li key={index} style={{ marginBottom: 8 }}>
                      <label>
                        <input
                          type="checkbox"
                          checked={selecionados.includes(ficheiro)}
                          onChange={() => handleCheckboxChange(ficheiro)}
                          style={{ marginRight: 8 }}
                        />
                        {ficheiro}
                      </label>
                    </li>
                  ))}
                </ul>
              )}

              <div style={{ textAlign: 'center' }}>
                <button
                  onClick={confirmarFicheiros}
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
                  Confirmar Ficheiros
                </button>
              </div>
            </>
          )}

          {mensagem && (
            <p style={{ marginTop: 20, fontWeight: 'bold', textAlign: 'center' }}>{mensagem}</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default UploadPage;
