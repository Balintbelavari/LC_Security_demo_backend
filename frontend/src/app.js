import React, { useState } from "react";
import "./app.css";
import logo from "./assets/lc_security_logo.png";

function App() {
  const [message, setMessage] = useState("");
  const [prediction, setPrediction] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handlePredict = async () => {
    if (!message.trim()) {
      setError("Error: Message cannot be empty");
      return;
    }

    try {
      setError("");
      setPrediction("");
      setLoading(true);
      const response = await fetch(
        "https://lc-security-backend-d51e9de3f86b.herokuapp.com/predict",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          `Failed to fetch prediction: ${
            errorData.detail || response.statusText
          }`
        );
      }

      const data = await response.json();
      setPrediction(data.prediction);
    } catch (err) {
      setError("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="header">
        <img src={logo} alt="LC Security Logo" className="logo" />
        <span className="header-text">LC Security</span>
      </div>
      <h1>
        Is it a <span className="highlight">scam</span>?
      </h1>
      <div className="input-container">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type something here..."
          rows="1" // Default to 1 row
          style={{
            height: "32px", // Default height
            minHeight: "20px", // Ensures single-row height
            maxHeight: "160px",
            overflowY: "auto",
          }}
          onInput={(e) => {
            e.target.style.height = "20px"; // Reset before recalculating
            if (e.target.scrollHeight > 20) {
              e.target.style.height =
                Math.min(e.target.scrollHeight, 160) + "px";
            }
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handlePredict();
            }
          }}
        />
        <button onClick={handlePredict} disabled={loading}>
          Check
        </button>
      </div>
      {loading && <p>Loading...</p>}
      {prediction && (
        <p className="prediction">
          Prediction: <strong>{prediction}</strong>
        </p>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  );
}

export default App;
