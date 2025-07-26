import React from "react";
import { useNavigate } from "react-router-dom";
import "./Navbar.css";
import logoUPT from "../assets/logoUPT.png";
import logoutIcon from "../assets/logout.png"; // ícone de logout (coloca-o em /assets)

function Navbar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.clear(); // limpa dados guardados
    navigate("/");        // vai para a página de login
  };

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <img
          src={logoUPT}
          alt="Logo UPT"
          className="navbar-logo"
        />
      </div>

      <div className="navbar-center">
        <ul>
          <li>Portais</li>
          <li>Docente</li>
          <li>Estudante</li>
          <li>Suporte</li>
          <li>Decisão</li>
        </ul>
      </div>

      <div className="navbar-right">
        <select>
          <option>Português</option>
          <option>English</option>
        </select>
        <img
          src={logoutIcon}
          alt="Logout"
          title="Terminar Sessão"
          onClick={handleLogout}
          style={{
            height: 28,
            width: 28,
            marginLeft: 12,
            cursor: "pointer"
          }}
        />
      </div>
    </nav>
  );
}

export default Navbar;
