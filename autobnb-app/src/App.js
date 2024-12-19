import React from "react";
import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom";
import { Container, Box, Typography } from "@mui/material";
import Form from "./components/Form";
import Key from "./components/Key";
import Results from './components/Results';
import bgImage from './assets/bg.avif';

const AppContent = () => {
  const location = useLocation();
  const isHomePage = location.pathname === '/';

  return (
    <Box sx={{
      width: '100%',
      minHeight: '100vh',
      backgroundImage: `url(${bgImage})`,
      backgroundPosition: 'center',
      backgroundRepeat: 'repeat'
    }}>
      <Container
        style={{
          width: "100vw",
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: isHomePage ? "center" : "flex-start",
          paddingTop: isHomePage ? "0px" : "120px"
        }}
      >
        <Typography
          variant="h4"
          sx={{
            fontWeight: "bold",
            textAlign: "center",
            color: "#FF5A5F",
            marginBottom: "20px",
            paddingTop: isHomePage ? "0px" : "0px",
            backgroundColor: "white",
            padding: "20px 40px",
            borderRadius: "15px",
            boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)"
          }}
        >
          AutoBnb: Airbnb Query Search
        </Typography>

        <Key />
        
        <Box sx={{ width: '100%' }}>
          <Routes>
            <Route path="/" element={<Form />} />
            <Route path="/results" element={<Results />} />
          </Routes>
        </Box>
      </Container>
    </Box>
  );
};

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
