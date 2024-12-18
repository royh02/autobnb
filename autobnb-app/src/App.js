import React from "react";
import { Container, Typography, Box } from "@mui/material";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Form from "./components/Form";
import Results from './components/Results';

function App() {
  return (
    <Router>
      <Container
        maxWidth="sm"
        style={{
          height: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Box
          sx={{
            width: "100%",
            backgroundColor: "#fff",
            padding: 3,
            borderRadius: 2,
            boxShadow: 3,
          }}
        >
          {/* <Typography variant="h4" component="h1" gutterBottom align="center">
            AutoBnb: Airbnb Query Search
          </Typography> */}
          <Routes>
            <Route path="/" element={<Form />} />
            <Route path="/results" element={<Results />} />
          </Routes>
        </Box>
      </Container>
    </Router>
  );
}

export default App;
