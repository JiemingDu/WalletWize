import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";

// If you renamed files, pick ONE to render (Questionnaire or App)
import Questionnaire from "./pages/Questionnaire";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Questionnaire />
  </React.StrictMode>
);