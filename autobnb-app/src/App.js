import React from "react";
import { Container, Typography, Box } from "@mui/material";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Form from "./components/Form";
import Results from './components/Results';

function App() {
  return (
    <Router>
      <Container
        style={{
          width: "100vw",
          height: "100vh",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Typography
          variant="h4"
          sx={{
            fontWeight: "bold",
            textAlign: "center",
            color: "#FF5A5F",
            marginBottom: "20px",
          }}
        >
          AutoBnb: Airbnb Query Search
        </Typography>
        
        <Routes>
          <Route path="/" element={<Form />} />
          <Route path="/results" element={<Results />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App;
