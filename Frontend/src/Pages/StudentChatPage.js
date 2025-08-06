import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function StudentChatPage() {
  const [aluno, setAluno] = useState(null);
  const [cadeira, setCadeira] = useState('');
  const [mensagem, setMensagem] = useState('');
  const [conversa, setConversa] = useState([]);
  const [ficheiros, setFicheiros] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const alunoLogado = JSON.parse(localStorage.getItem('alunoLogado'));
    const cadeiraSelecionada = localStorage.getItem('cadeiraSelecionada');

    if (!alunoLogado || !cadeiraSelecionada) {
      navigate('/');
    } else {
      setAluno(alunoLogado);
      setCadeira(cadeiraSelecionada);
    }
  }, [navigate]);

  useEffect(() => {
    if (cadeira) {
      fetch(`http://localhost:8000/ficheiros_confirmados?cadeira=${cadeira}`)
        .then((res) => res.json())
        .then((data) => {
          setFicheiros(data.ficheiros || []);
        })
        .catch((err) => {
          console.error("Erro ao buscar ficheiros confirmados:", err);
          setFicheiros([]);
        });
    }
  }, [cadeira]);

  const enviarMensagem = async (msg) => {
    if (msg.trim() === '') return;

    setConversa(prev => [...prev, { texto: msg, autor: 'aluno' }]);
    setConversa(prev => [...prev, { texto: "⏳ A responder...", autor: 'bot' }]);

    try {
      const response = await fetch('http://127.0.0.1:8000/perguntar', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          pergunta: msg,
          cadeira: cadeira
        })
      });

      const data = await response.json();

      setConversa(prev => prev.filter(m => m.texto !== "⏳ A responder..."));
      setConversa(prev => [...prev, { texto: data.resposta, autor: 'bot' }]);

    } catch (error) {
      console.error('Erro ao contactar o backend:', error);
      setConversa(prev => prev.filter(m => m.texto !== "⏳ A responder..."));
      setConversa(prev => [...prev, { texto: '⚠️ Erro ao contactar o servidor.', autor: 'bot' }]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const msgAtual = e.target.value;
      if (msgAtual.trim() !== '') {
        enviarMensagem(msgAtual);
        setMensagem('');
      }
    }
  };

  const voltarDashboard = () => {
    navigate('/estudante');
  };

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'Arial' }}>
      {/* COLUNA DO CHAT */}
      <div style={{ flex: 2, padding: 20, borderRight: '1px solid #ccc' }}>
        <h2>🤖 Chatbot da cadeira: {cadeira}</h2>
        <p><strong>Estudante:</strong> {aluno?.nome}</p>

        <div style={{
          border: '1px solid #ccc',
          height: '60vh',
          padding: 10,
          overflowY: 'auto',
          background: '#f9f9f9',
          borderRadius: 6,
          marginTop: 10
        }}>
          {conversa.map((m, i) => (
            <div key={i} style={{ textAlign: m.autor === 'aluno' ? 'right' : 'left', margin: '5px 0' }}>
              <span style={{
                background: m.autor === 'aluno' ? '#d0eaff' : '#eee',
                padding: 8,
                borderRadius: 6,
                display: 'inline-block',
                maxWidth: '70%'
              }}>
                {m.texto}
              </span>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 10, display: 'flex' }}>
          <input
            type="text"
            placeholder="Escreve a tua mensagem..."
            value={mensagem}
            onChange={e => setMensagem(e.target.value)}
            onKeyDown={handleKeyDown}
            style={{ flex: 1, padding: 8 }}
          />
          <button
            onClick={() => {
              enviarMensagem(mensagem);
              setMensagem('');
            }}
            style={{
              padding: '8px 16px',
              marginLeft: 10,
              background: 'royalblue',
              color: 'white',
              border: 'none',
              borderRadius: 5
            }}
          >
            Enviar
          </button>
        </div>

        <button
          onClick={voltarDashboard}
          style={{
            marginTop: 20,
            background: 'white',
            color: 'black',
            border: '1px solid #ccc',
            padding: '8px 16px',
            borderRadius: 5,
            cursor: 'pointer'
          }}
        >
          Voltar ao Dashboard
        </button>
      </div>

      {/* COLUNA DOS FICHEIROS */}
      <div style={{
        flex: 1,
        padding: 30,
        backgroundColor: '#e0e0e0',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center'
      }}>
        <h3 style={{ marginBottom: 15 }}>📁 Ficheiros de {cadeira}</h3>
        {ficheiros.length > 0 ? (
          <ul style={{ paddingLeft: 20 }}>
            {ficheiros.map((f, i) => (
              <li key={i} style={{ marginBottom: 8 }}>
                <a
                  href={f.caminho}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {f.nome}
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <p>Não há ficheiros disponíveis.</p>
        )}
      </div>
    </div>
  );
}

export default StudentChatPage;
