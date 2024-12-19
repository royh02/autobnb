import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, Button, AppBar, Toolbar, Container, Link, CircularProgress, IconButton, Grid } from "@mui/material";
import { useNavigate, useLocation, Navigate } from 'react-router-dom';
import HomeIcon from '@mui/icons-material/Home';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

const Results = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Check if we have data in the location state
  if (!location.state || !location.state.data) {
    return <Navigate to="/" replace />;
  }

  const listings = location.state.data;

  return (
    <Box sx={{ 
      width: '100%', 
      minHeight: '100vh', 
      bgcolor: 'background.default'
    }}>
      {/* Header */}
      <AppBar position="fixed" sx={{ bgcolor: 'white' }}>
        <Toolbar>
          <Button
            onClick={() => navigate('/')}
            startIcon={<ArrowBackIcon />}
            sx={{ color: '#FF5A5F' }}
          >
            Back to Search
          </Button>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ pt: 10, pb: 4 }}>
        <Grid container spacing={3}>
          {listings.map((listing, index) => (
            <Grid item xs={12} md={6} key={listing.url}>
              <ListingCell url={listing.url} rank={index + 1} summary={listing.summary} />
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
};

const ListingCell = ({ url, rank, summary }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [images, setImages] = useState([]);
  const fetchedRef = useRef(false);

  useEffect(() => {
    const loadImages = async () => {
      if (fetchedRef.current) return;
      fetchedRef.current = true;
      
      try {
        setIsLoading(true);
        const response = await fetch(`http://127.0.0.1:5001/preview/${encodeURIComponent(url)}`);
        if (response.ok) {
          const imageUrls = await response.json();
          if (imageUrls && imageUrls.length > 0) {
            setImages(imageUrls);
          } else {
            setHasError(true);
          }
        } else {
          setHasError(true);
        }
      } catch (error) {
        console.error('Error fetching images:', error);
        setHasError(true);
      } finally {
        setIsLoading(false);
      }
    };

    loadImages();
  }, [url]);

  const handlePrevImage = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setCurrentImageIndex((prev) => (prev > 0 ? prev - 1 : images.length - 1));
  };

  const handleNextImage = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setCurrentImageIndex((prev) => (prev < images.length - 1 ? prev + 1 : 0));
  };

  return (
    <Box
      sx={{
        position: 'relative',
        width: '100%',
        bgcolor: 'background.paper',
        borderRadius: 2,
        overflow: 'hidden',
        boxShadow: 3,
      }}
    >
      {/* Rank Badge */}
      <Box
        sx={{
          position: 'absolute',
          top: 10,
          left: 10,
          zIndex: 2,
          display: 'flex',
          alignItems: 'center',
          bgcolor: 'rgba(255, 255, 255, 0.9)',
          borderRadius: '12px',
          padding: '4px 8px',
          boxShadow: 2,
        }}
      >
        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
          #{rank}
        </Typography>
      </Box>

      {/* Image Container */}
      <Box
        sx={{
          position: 'relative',
          width: '100%',
          height: '400px',
          bgcolor: '#f5f5f5',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Loading Spinner */}
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

        {/* Images */}
        {images.map((imageUrl, index) => (
          <Box
            key={imageUrl}
            component="img"
            src={imageUrl}
            alt={`Listing image ${index + 1}`}
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: currentImageIndex === index ? 1 : 0,
              transition: 'opacity 0.3s ease-in-out',
            }}
          />
        ))}

        {/* Fallback Icon */}
        {!isLoading && (hasError || images.length === 0) && (
          <HomeIcon sx={{ fontSize: 48, color: '#bbb' }} />
        )}

        {/* Navigation Arrows */}
        {images.length > 1 && (
          <>
            <IconButton
              onClick={handlePrevImage}
              sx={{
                position: 'absolute',
                left: 8,
                top: '50%',
                transform: 'translateY(-50%)',
                bgcolor: 'rgba(255, 255, 255, 0.9)',
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 1)',
                },
                zIndex: 2,
              }}
            >
              <ChevronLeftIcon />
            </IconButton>
            <IconButton
              onClick={handleNextImage}
              sx={{
                position: 'absolute',
                right: 8,
                top: '50%',
                transform: 'translateY(-50%)',
                bgcolor: 'rgba(255, 255, 255, 0.9)',
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 1)',
                },
                zIndex: 2,
              }}
            >
              <ChevronRightIcon />
            </IconButton>

            {/* Image Indicators */}
            <Box
              sx={{
                position: 'absolute',
                bottom: 8,
                left: '50%',
                transform: 'translateX(-50%)',
                display: 'flex',
                gap: 1,
                zIndex: 2,
              }}
            >
              {images.map((_, index) => (
                <Box
                  key={index}
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    bgcolor: currentImageIndex === index ? 'white' : 'rgba(255, 255, 255, 0.5)',
                    transition: 'background-color 0.3s ease-in-out',
                  }}
                />
              ))}
            </Box>
          </>
        )}
      </Box>

      {/* Content Area */}
      <Box
        sx={{
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        {/* Summary */}
        <Typography
          variant="body1"
          sx={{
            color: 'text.secondary',
            lineHeight: 1.6,
          }}
        >
          {summary}
        </Typography>

        {/* View on Airbnb Link */}
        <Link
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          sx={{
            color: '#FF5A5F',
            textDecoration: 'none',
            fontWeight: 'bold',
            '&:hover': {
              textDecoration: 'underline',
            },
          }}
        >
          <Typography
            variant="h6"
            sx={{
              fontWeight: 'bold',
              color: '#FF5A5F',
            }}
          >
            View on Airbnb
          </Typography>
        </Link>
      </Box>
    </Box>
  );
};

export default Results;
