import React from "react";
import "../css/Navbar.css";

const Navbar = () => {
  return (
    <div className="navbar-container">
      <div className="logo">
        <img src="/logo_placespeak.png" alt="logo"></img>
      </div>
      <div className="title">
        <span>Report Generator</span>
      </div>
      <div className="buttons">
        <button type="button" className="btn btn-primary btn-sm">
          Preview
        </button>
        <button type="button" className="btn btn-secondary btn-sm">
          Exit Admin
        </button>
      </div>
    </div>
  );
};

export default Navbar;
