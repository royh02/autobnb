import React, { useState } from "react";
import {
  Button,
  Box,
  Typography,
  MenuItem,
  FormControlLabel,
  Checkbox,
} from "@mui/material";
import FormField from "./FormField";

const amenitiesList = ["Kitchen", "Pool", "WiFi", "Washer", "Parking", "Gym"];
const viewsList = ["Bay", "Ocean", "Beach", "Garden", "Marina", "City"];

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

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formValues.location) {
      alert("Location is mandatory.");
      return;
    }
    console.log("Form submitted:", formValues);
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ display: "flex", flexDirection: "column", gap: 2 }}
    >
      <FormField
        label="Location *"
        name="location"
        value={formValues.location}
        onChange={handleChange}
        required
      />
      <FormField
        label="Check-In Date"
        name="checkIn"
        type="date"
        value={formValues.checkIn}
        onChange={handleChange}
        InputLabelProps={{ shrink: true }}
      />
      <FormField
        label="Check-Out Date"
        name="checkOut"
        type="date"
        value={formValues.checkOut}
        onChange={handleChange}
        InputLabelProps={{ shrink: true }}
      />
      <FormField
        label="Number of Guests"
        name="guests"
        type="number"
        value={formValues.guests}
        onChange={handleChange}
      />
      <Box sx={{ display: 'flex', gap: 2 }}>
        <FormField
          label="Min Price"
          name="priceMin"
          type="number"
          value={formValues.priceMin}
          onChange={handleChange}
          InputProps={{
            startAdornment: "$"
          }}
        />
        <FormField
          label="Max Price"
          name="priceMax"
          type="number"
          value={formValues.priceMax}
          onChange={handleChange}
          InputProps={{
            startAdornment: "$"
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
        />
        <FormField
          label="Bathrooms"
          name="bathrooms"
          type="number"
          value={formValues.bathrooms}
          onChange={handleChange}
          InputProps={{ inputProps: { min: 1 } }}
        />
      </Box>
      <Box>
        <Typography variant="subtitle1" gutterBottom>
          Amenities
        </Typography>
        {amenitiesList.map((amenity) => (
          <FormControlLabel
            key={amenity}
            control={
              <Checkbox
                value={amenity}
                checked={formValues.amenities.includes(amenity)}
                onChange={(e) => handleCheckboxChange(e, "amenities")}
              />
            }
            label={amenity}
          />
        ))}
      </Box>
      <Box>
        <Typography variant="subtitle1" gutterBottom>
          Views
        </Typography>
        {viewsList.map((view) => (
          <FormControlLabel
            key={view}
            control={
              <Checkbox
                value={view}
                checked={formValues.views.includes(view)}
                onChange={(e) => handleCheckboxChange(e, "views")}
              />
            }
            label={view}
          />
        ))}
      </Box>
      <Box>
        <Typography variant="subtitle1" gutterBottom>
          Additional Details
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Describe the vibe or any extra details you're looking for
        </Typography>
        <FormField
          name="additionalInfo"
          value={formValues.additionalInfo}
          onChange={handleChange}
          multiline
          rows={4}
          fullWidth
        />
      </Box>
      <Button type="submit" variant="contained" color="primary" fullWidth>
        Search
      </Button>
    </Box>
  );
};

export default Form;

// add price range, number of bed and bath
// additional info large text field, subheader vibe or extra details

// format only default fields as good instruction for web surfer agent, use fedfault search filter mechanism, format as a task
