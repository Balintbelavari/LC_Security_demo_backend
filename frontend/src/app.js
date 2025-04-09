import React, { useState } from "react";
import "./app.css";
import logo from "./assets/lc_security_logo.png";

function App() {
  const [message, setMessage] = useState("");
  const [prediction, setPrediction] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [useBert, setUseBert] = useState(true); // State to track model selection

  const handlePredict = async (inputMessage) => {
    const text = inputMessage || message; // Use the provided example or typed input

    if (!text.trim()) {
      setError("Error: Message cannot be empty");
      return;
    }

    try {
      setError("");
      setPrediction("");
      setLoading(true);
      setMessage(text); // Set message state for example buttons

      // Make the fetch request with both the message and use_bert
      const response = await fetch(
        "https://lc-security-backend-d51e9de3f86b.herokuapp.com/predict",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: text,
            use_bert: useBert, // Include use_bert in the request body
          }),
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
          rows="1"
          style={{
            height: "32px",
            minHeight: "20px",
            maxHeight: "160px",
            overflowY: "auto",
          }}
          onInput={(e) => {
            e.target.style.height = "20px";
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

        <div className="model-selection">
          <button onClick={() => handlePredict()} disabled={loading}>
            Check
          </button>
          <select
            id="model-select"
            value={useBert ? "bert" : "traditional"}
            onChange={(e) => setUseBert(e.target.value === "bert")}
          >
            <option value="bert">BERT Model (new)</option>
            <option value="traditional">Naive-Bayes Model (old)</option>
          </select>
        </div>
      </div>

      {loading && <p>Loading...</p>}
      {prediction && (
        <p
          className={`prediction ${
            prediction === "ham" ? "text-green-600" : "text-red-600"
          }`}
        >
          {prediction === "ham" ? (
            <>
              Prediction: <strong>Safe ✅</strong>
            </>
          ) : (
            <>
              Prediction: <strong>Harmful 🚨</strong>
            </>
          )}
        </p>
      )}
      {error && <p className="error">{error}</p>}

      {/* Example Messages Section */}
      <div className="example-container">
        <p className="example-title">Try these:</p>
        <div className="example-buttons">
          <button
            className="example-button"
            onClick={() =>
              handlePredict(
                "Congratulations on Your Admission to the University of Debrecen!"
              )
            }
          >
            Congratulations on Your Admission to the University of Debrecen!
          </button>
          <button
            className="example-button"
            onClick={() =>
              handlePredict(
                "You won! As a valued Vodafone customer, our computer has picked you to win $150. To collect, it's easy, just call +09061743386"
              )
            }
          >
            You won! As a valued Vodafone customer, our computer has picked you
            to win $150. To collect, it's easy, just call +09061743386
          </button>
        </div>
      </div>

      {/* Version Section */}
      <div className="version-container">
        <p className="version-label">Newest Model Version: 0.2.2</p>
      </div>
    </div>
  );
}

export default App;
