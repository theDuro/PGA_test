const Button = ({ onClick, children }) => {
  return (
    <button className="menu-btn" onClick={onClick}>
      {children}
    </button>
  );
};

export default Button;