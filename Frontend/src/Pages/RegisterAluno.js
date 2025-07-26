import React, { useState, useEffect } from 'react';
import { cursos } from './CursosECadeiras';

function RegisterAluno() {
  const [form, setForm] = useState({
    nome: '',
    email: '',
    password: '',
    curso: '',
    cadeiras: []
  });

  const [cadeirasDisponiveis, setCadeirasDisponiveis] = useState([]);
  const [sucesso, setSucesso] = useState(false);

  useEffect(() => {
    if (form.curso) {
      setCadeirasDisponiveis(cursos[form.curso]);
    } else {
      setCadeirasDisponiveis([]);
    }
  }, [form.curso]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleCheckbox = (cadeira) => {
    setForm((prev) => {
      const jaSelecionada = prev.cadeiras.includes(cadeira);
      const novaLista = jaSelecionada
        ? prev.cadeiras.filter((c) => c !== cadeira)
        : [...prev.cadeiras, cadeira];
      return { ...prev, cadeiras: novaLista };
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const alunos = JSON.parse(localStorage.getItem('alunos')) || [];
    if (alunos.find((a) => a.email === form.email)) {
      alert('Já existe um aluno com este email.');
      return;
    }
    alunos.push(form);
    localStorage.setItem('alunos', JSON.stringify(alunos));
    setSucesso(true);
    setForm({ nome: '', email: '', password: '', curso: '', cadeiras: [] });
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6 flex justify-center items-center">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-xl space-y-6">
        <h2 className="text-2xl font-bold text-blue-700">Registo de Aluno</h2>

        <input name="nome" value={form.nome} onChange={handleChange} placeholder="Nome"
          className="w-full border p-2 rounded-lg" required />

        <input name="email" type="email" value={form.email} onChange={handleChange} placeholder="Email"
          className="w-full border p-2 rounded-lg" required />

        <input name="password" type="password" value={form.password} onChange={handleChange} placeholder="Password"
          className="w-full border p-2 rounded-lg" required />

        <select name="curso" value={form.curso} onChange={handleChange} className="w-full border p-2 rounded-lg" required>
          <option value="">Seleciona um curso</option>
          {Object.keys(cursos).map((curso) => (
            <option key={curso} value={curso}>{curso}</option>
          ))}
        </select>

        {cadeirasDisponiveis.length > 0 && (
          <div>
            <p className="font-semibold">Seleciona as cadeiras:</p>
            <div className="grid grid-cols-2 gap-2 mt-2">
              {cadeirasDisponiveis.map((c) => (
                <label key={c} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={form.cadeiras.includes(c)}
                    onChange={() => handleCheckbox(c)}
                    className="mr-2"
                  />
                  {c}
                </label>
              ))}
            </div>
          </div>
        )}

        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
          Registar
        </button>

        {sucesso && <p className="text-green-600 font-medium">✅ Aluno registado com sucesso!</p>}
      </form>
    </div>
  );
}

export default RegisterAluno;