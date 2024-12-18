import React, { useState } from 'react';
import { Box, Typography, Button, AppBar, Toolbar, Container, Link, Tooltip, CircularProgress } from "@mui/material";
import { useNavigate, useLocation } from 'react-router-dom';
import HomeIcon from '@mui/icons-material/Home';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

const Results = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [hoveredUrl, setHoveredUrl] = useState(null);
  const [loadingImages, setLoadingImages] = useState({});

  const urls = location.state?.urls || [];

  const handleBack = () => {
    navigate('/');
  };

  const PreviewTooltip = ({ url }) => {
    const [isLoading, setIsLoading] = useState(true);
    const [hasError, setHasError] = useState(false);

    return (
      <Box
        sx={{
          width: 400,
          height: 300,
          bgcolor: 'background.paper',
          borderRadius: 2,
          overflow: 'hidden',
          boxShadow: 3,
          position: 'relative',
        }}
      >
        {isLoading && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: 'rgba(255, 255, 255, 0.8)',
              zIndex: 1,
            }}
          >
            <CircularProgress />
          </Box>
        )}
        <Box
          component="img"
          src={`http://127.0.0.1:5001/preview/${encodeURIComponent(url)}`}
          onLoad={() => setIsLoading(false)}
          onError={() => {
            setIsLoading(false);
            setHasError(true);
          }}
          sx={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            display: hasError ? 'none' : 'block',
          }}
        />
        {hasError && (
          <Box
            sx={{
              width: '100%',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: '#f5f5f5',
            }}
          >
            <HomeIcon sx={{ fontSize: 48, color: '#bbb' }} />
          </Box>
        )}
      </Box>
    );
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f7f7f7' }}>
      {/* Header */}
      <AppBar position="fixed" sx={{ bgcolor: 'white', boxShadow: '0 2px 4px rgba(0,0,0,0.08)' }}>
        <Toolbar>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/')}
            sx={{
              color: '#FF5A5F',
              '&:hover': {
                bgcolor: 'rgba(255,90,95,0.1)'
              }
            }}
          >
            Back to Search
          </Button>
          <Box sx={{ flexGrow: 1 }} />
          <HomeIcon sx={{ color: '#FF5A5F', fontSize: 28 }} />
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ pt: 10, pb: 4 }}>
        {/* Results Header */}
        <Box sx={{ mb: 4, mt: 2 }}>
          <Typography variant="h5" sx={{ fontWeight: 600, color: '#222' }}>
            {urls.length} stays found
          </Typography>
          <Typography variant="body1" sx={{ color: '#717171', mt: 1 }}>
            Explore unique places to stay
          </Typography>
        </Box>

        {/* Results Grid */}
        <Box sx={{ 
          display: 'grid',
          gridTemplateColumns: '1fr', // Default for mobile
          gap: 3,
          '@media (min-width: 600px)': {
            gridTemplateColumns: 'repeat(2, 1fr)', // 2 columns on tablet
          },
          '@media (min-width: 960px)': {
            gridTemplateColumns: 'repeat(3, 1fr)', // 3 columns on desktop
          },
          maxWidth: '100%',
          margin: '0 auto'
        }}>
          {urls.map((url, index) => (
            <Tooltip
              key={index}
              title={<PreviewTooltip url={url} />}
              placement="right"
              arrow
              followCursor
              PopperProps={{
                sx: {
                  '& .MuiTooltip-tooltip': {
                    bgcolor: 'transparent',
                    p: 0
                  },
                  '& .MuiTooltip-arrow': {
                    color: 'background.paper'
                  }
                }
              }}
            >
              <Box
                component="a"
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                sx={{
                  textDecoration: 'none',
                  color: 'inherit',
                  display: 'block',
                  borderRadius: 3,
                  overflow: 'hidden',
                  transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 16px rgba(0,0,0,0.1)',
                  }
                }}
              >
                {/* Placeholder Image */}
                <Box sx={{
                  bgcolor: '#f0f0f0',
                  paddingTop: '66.67%', // 3:2 aspect ratio
                  position: 'relative',
                  borderRadius: 3,
                  overflow: 'hidden',
                }}>
                  <Box sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: '#e1e1e1',
                  }}>
                    <HomeIcon sx={{ fontSize: 48, color: '#bbb' }} />
                  </Box>
                </Box>

                {/* URL Text Container */}
                <Box
                  sx={{
                    mt: 2,
                    px: 2.5, // Increased horizontal padding
                    pb: 2.5,  // Added bottom padding
                    pt: 1.5,  // Added top padding
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    wordBreak: 'break-word'
                  }}
                >
                  <Link
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    sx={{
                      color: 'text.primary',
                      textDecoration: 'none',
                      '&:hover': {
                        textDecoration: 'underline',
                      },
                      fontSize: '0.95rem',
                      lineHeight: 1.4,
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden'
                    }}
                  >
                    {url}
                  </Link>
                </Box>
              </Box>
            </Tooltip>
          ))}
        </Box>
      </Container>
    </Box>
  );
};

export default Results;
