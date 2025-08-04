// Base de dados fictícia: cursos e cadeiras

export const cursos = {
  "Engenharia Informática": [
    "",
    "Inteligência Artificial",
    "Programação Web"
  ],
  "Ciências da Computação": [
    "Redes de Computadores",
    "Visão por Computador",
    "Criptografia"
  ],
  "Engenharia Biomédica": [
    "Bioinformática",
    "Processamento de Sinal",
    "Modelação Biomédica"
  ]
};

// Professores iniciais
export const professoresIniciais = [
  {
    nome: "Ana Silva",
    email: "ana.silva@upt.pt",
    password: "ana123",
    curso: "Engenharia Informática",
    cadeiras: ["Sistemas Distribuídos"]
  },
  {
    nome: "Carlos Ribeiro",
    email: "carlos.ribeiro@upt.pt",
    password: "carlos123",
    curso: "Ciências da Computação",
    cadeiras: ["Visão por Computador"]
  },
  {
    nome: "Diana Costa",
    email: "diana.costa@upt.pt",
    password: "diana123",
    curso: "Engenharia Biomédica",
    cadeiras: ["Bioinformática"]
  }
];

// Alunos iniciais
export const alunosIniciais = [
  {
    nome: "João Lopes",
    email: "joao.lopes@upt.pt",
    password: "joao123",
    curso: "Engenharia Informática",
    cadeiras: ["Sistemas Distribuídos"]
  },
  {
    nome: "Maria Santos",
    email: "maria.santos@upt.pt",
    password: "maria123",
    curso: "Ciências da Computação",
    cadeiras: ["Redes de Computadores"]
  },
  {
    nome: "Bruno Rocha",
    email: "bruno.rocha@upt.pt",
    password: "bruno123",
    curso: "Engenharia Biomédica",
    cadeiras: ["Bioinformática"]
  }
];