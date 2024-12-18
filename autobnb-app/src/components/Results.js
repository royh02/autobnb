import React from 'react';
import { Box, Typography, Button } from "@mui/material";
import { useNavigate, useLocation } from 'react-router-dom';

const Results = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const urls = location.state?.urls || [];

  return (
    <Box sx={{ 
      p: 4,
      maxWidth: 1200,
      margin: "auto",
    }}>
      <Box sx={{ 
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        mb: 4
      }}>
        <Typography
          variant="h4"
          sx={{
            fontWeight: "bold",
            color: "#FF5A5F",
          }}
        >
          Found {urls.length} Listings
        </Typography>
        <Button
          onClick={() => navigate('/')}
          variant="outlined"
          sx={{
            color: "#FF5A5F",
            borderColor: "#FF5A5F",
            "&:hover": {
              borderColor: "#FF3B39",
              backgroundColor: "rgba(255,90,95,0.1)"
            }
          }}
        >
          New Search
        </Button>
      </Box>

      <Box sx={{ 
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        gap: 3,
        p: 2,
        bgcolor: "#f7f7f7",
        borderRadius: "12px",
        minHeight: "calc(100vh - 200px)"
      }}>
        {urls.map((url, index) => (
          <Box 
            key={index}
            component="a"
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            sx={{
              display: 'block',
              p: 3,
              bgcolor: "white",
              borderRadius: "12px",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
              transition: "all 0.2s ease-in-out",
              textDecoration: "none",
              color: "#FF5A5F",
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: "0 4px 8px rgba(0,0,0,0.15)",
                bgcolor: "rgba(255,90,95,0.05)"
              }
            }}
          >
            <Typography 
              variant="h6" 
              sx={{ 
                fontSize: "1.1rem",
                fontWeight: "500",
                textAlign: "center"
              }}
            >
              Listing {index + 1}
            </Typography>
            <Typography 
              variant="body2" 
              sx={{ 
                color: "#666",
                mt: 1,
                textAlign: "center",
                fontSize: "0.875rem"
              }}
            >
              Click to view on Airbnb
            </Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default Results;
