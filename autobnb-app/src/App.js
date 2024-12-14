import React from "react";
import { Container, Typography, Box } from "@mui/material";
import Form from "./components/Form";

const App = () => {
  return (
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
        <Typography variant="h4" component="h1" gutterBottom align="center">
          AutoBnb: Airbnb Query Search
        </Typography>
        <Form />
      </Box>
    </Container>
  );
};

export default App;
