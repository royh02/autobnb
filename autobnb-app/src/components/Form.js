import React, { useState } from "react";
import {
  Button,
  Box,
  Typography,
  FormControlLabel,
  Checkbox,
  InputAdornment,
} from "@mui/material";
import FormField from "./FormField";

const amenitiesList = ["Kitchen", "Pool", "WiFi", "Washer", "Parking", "Gym"];
const viewsList = ["Bay", "Ocean", "Beach", "Garden", "Marina", "City"];

const formatSearchQuery = (formData) => {
  const structuredData = {
    location: formData.location,
    dates: {
      checkIn: formData.checkIn || null,
      checkOut: formData.checkOut || null
    },
    guests: formData.guests,
    price: {
      minimum: formData.priceMin || 0,
      maximum: formData.priceMax || 999999999,
    },
    rooms: {
      bedrooms: formData.bedrooms,
      bathrooms: formData.bathrooms
    },
    amenities: formData.amenities,
    views: formData.views,
    additionalPreferences: formData.additionalInfo.trim() || null
  };
  return structuredData;
};

const Form = () => {
  const [formValues, setFormValues] = useState({
    location: "",
    checkIn: "",
    checkOut: "",
    guests: 1,
    priceMin: "",
    priceMax: "",
    bedrooms: 1,
    bathrooms: 1,
    additionalInfo: "",
    amenities: [],
    views: [],
  });

  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleCheckboxChange = (e, category) => {
    const { value, checked } = e.target;
    setFormValues((prev) => ({
      ...prev,
      [category]: checked
        ? [...prev[category], value]
        : prev[category].filter((item) => item !== value),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const query = formatSearchQuery(formValues);
    setSubmitted(true);

    try {
      const response = await fetch('http://127.0.0.1:5001/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });
      
      if (!response.ok) {
        throw new Error('Search request failed');
      }
      
      const data = await response.json();
      console.log('Search response:', data);
      setSubmitted(true);
    } catch (error) {
      console.error('Error during search:', error);
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        display: "flex",
        flexDirection: "column",
        gap: 3,
        maxWidth: 1200, 
        margin: "auto",
        padding: 4,
        backgroundColor: "#fff",
        borderRadius: 6,
        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
        maxHeight: '80vh',
        overflow: 'auto',
      }}
    >
      <Typography
        variant="h4"
        color="primary"
        sx={{
          fontWeight: "bold",
          textAlign: "center",
          color: "#FF5A5F", 
        }}
      >
        AutoBnb: Airbnb Query Search
      </Typography>
      
      {submitted ? (
        <Typography variant="h6" sx={{ textAlign: "center" }}>
          Success! Your search has been submitted.
        </Typography>
      ) : (
        <>
          <FormField
            label="Location"
            name="location"
            value={formValues.location}
            onChange={handleChange}
            required
            InputLabelProps={{ shrink: true }}
            placeholder="Berkeley, CA"
            sx={{
              borderRadius: "8px",
              padding: "10px",
              backgroundColor: "#f7f7f7", // Light gray background for inputs
              boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
            }}
          />
          <FormField
            label="Check-In Date"
            name="checkIn"
            type="date"
            value={formValues.checkIn}
            onChange={handleChange}
            InputLabelProps={{ shrink: true }}
            sx={{
              borderRadius: "8px",
              padding: "10px",
              backgroundColor: "#f7f7f7",
              boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
            }}
          />
          <FormField
            label="Check-Out Date"
            name="checkOut"
            type="date"
            value={formValues.checkOut}
            onChange={handleChange}
            InputLabelProps={{ shrink: true }}
            sx={{
              borderRadius: "8px",
              padding: "10px",
              backgroundColor: "#f7f7f7",
              boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
            }}
          />
          <FormField
            label="Number of Guests"
            name="guests"
            type="number"
            value={formValues.guests}
            onChange={handleChange}
            sx={{
              borderRadius: "8px",
              padding: "10px",
              backgroundColor: "#f7f7f7",
              boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
            }}
          />
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <FormField
              label="Min Price"
              name="priceMin"
              type="number"
              value={formValues.priceMin}
              onChange={handleChange}
              InputProps={{
                startAdornment: <InputAdornment position="start">$</InputAdornment>
              }}
              sx={{
                borderRadius: "8px",
                padding: "10px",
                backgroundColor: "#f7f7f7",
                boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
              }}
            />
            <FormField
              label="Max Price"
              name="priceMax"
              type="number"
              value={formValues.priceMax}
              onChange={handleChange}
              InputProps={{
                startAdornment: <InputAdornment position="start">$</InputAdornment>
              }}
              sx={{
                borderRadius: "8px",
                padding: "10px",
                backgroundColor: "#f7f7f7",
                boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
              }}
            />
          </Box>

          <Box sx={{ display: 'flex', gap: 2 }}>
            <FormField
              label="Bedrooms"
              name="bedrooms"
              type="number"
              value={formValues.bedrooms}
              onChange={handleChange}
              InputProps={{ inputProps: { min: 1 } }}
              sx={{
                borderRadius: "8px",
                padding: "10px",
                backgroundColor: "#f7f7f7",
                boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
              }}
            />
            <FormField
              label="Bathrooms"
              name="bathrooms"
              type="number"
              value={formValues.bathrooms}
              onChange={handleChange}
              InputProps={{ inputProps: { min: 1 } }}
              sx={{
                borderRadius: "8px",
                padding: "10px",
                backgroundColor: "#f7f7f7",
                boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
              }}
            />
          </Box>

          <Box>
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', color: '#444' }}>
              Amenities
            </Typography>
            <Box sx={{
                borderRadius: "8px",
                padding: "10px",
                backgroundColor: "#f7f7f7",
                boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
              }}>

              {amenitiesList.map((amenity, index) => (
                <FormControlLabel
                  key={amenity}
                  control={
                    <Checkbox
                      id={`amenity-${index}`}
                      name="amenities" 
                      value={amenity}
                      checked={formValues.amenities.includes(amenity)}
                      onChange={(e) => handleCheckboxChange(e, "amenities")}
                      sx={{
                        color: "#444", 
                        '&.Mui-checked': {
                          color: "#FF5A5F", 
                        },
                        backgroundColor: "#f7f7f7",
                        borderRadius: "4px",
                        padding: "6px",
                      }}
                    />
                  }
                  label={amenity}
                />
              ))}
            </Box>
          </Box>

          <Box>
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', color: '#444' }}>
              Views
            </Typography>
            <Box sx={{
                borderRadius: "8px",
                padding: "10px",
                backgroundColor: "#f7f7f7",
                boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
              }}>

              {viewsList.map((view, index) => (
                <FormControlLabel
                  key={view}
                  control={
                    <Checkbox
                      id={`view-${index}`}
                      name="views" 
                      value={view}
                      checked={formValues.views.includes(view)}
                      onChange={(e) => handleCheckboxChange(e, "views")}
                      sx={{
                        color: "#444",
                        '&.Mui-checked': {
                          color: "#FF5A5F",
                        },
                        backgroundColor: "#f7f7f7",
                        borderRadius: "4px",
                        padding: "6px", 
                      }}
                    />
                  }
                  label={view}
                />
              ))}
            </Box>
          </Box>

          <Box>
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', color: '#444' }}>
              Additional Details
            </Typography>
            <FormField
              id="additionalInfo" 
              name="additionalInfo"
              value={formValues.additionalInfo}
              onChange={handleChange}
              multiline
              rows={4}
              fullWidth
              placeholder="cozy cabin vibe"
              sx={{
                borderRadius: "8px",
                padding: "10px",
                backgroundColor: "#f7f7f7",
                boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
              }}
            />
          </Box>

          <Button
            type="submit"
            variant="contained"
            color="primary"
            sx={{
              marginTop: 3,
              padding: "12px 24px",
              fontSize: "1rem",
              fontWeight: 'bold', 
              fontFamily: '"Circular", sans-serif',
              borderRadius: "8px",
              backgroundColor: "#FF5A5F", 
              color: "#ffffff", 
              '&:hover': {
                backgroundColor: "#FF3B39", 
              }
            }}
          >
            Search
          </Button>
        </>
      )}
    </Box>
  );
};

export default Form;
