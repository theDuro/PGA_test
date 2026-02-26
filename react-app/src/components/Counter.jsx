import { useState } from "react";

const Counter = () => {
  const [count, setCount] = useState(0);

  const increment = () => setCount((prev) => prev - 1); // w Vue było count.value-- więc odejmuje

  return (
    <div className="counter-wrapper">
      <p>Licznik: {count}</p>
      <button onClick={increment}>Dodaj 1</button>
    </div>
  );
};

export default Counter;