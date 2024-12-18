import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Button,
  Box,
  Typography,
  InputBase,
  styled,
  TextField,
} from "@mui/material";

// const amenitiesList = ["Kitchen", "Pool", "WiFi", "Washer", "Parking", "Gym"];
const amenitiesList = [
  "WiFi",
  "Kitchen",
  "Washer",
  "Dryer",
  "Free Parking",
  "Gym",
  "Pool",
];
// const viewsList = ["Bay", "Ocean", "Beach", "Garden", "Marina", "City"];

const formatSearchQuery = (formData) => {
  const url =
    "https://www.airbnb.com/s/" +
    formData.location +
    "/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes" +
    "&price_filter_input_type=2" +
    "&channel=EXPLORE" +
    "&date_picker_type=calendar" +
    (formData.checkIn ? "&checkin=" + formData.checkIn.toString() : "") +
    (formData.checkOut ? "&checkout=" + formData.checkOut.toString() : "") +
    (formData.guests.adults
      ? "&adults=" + formData.guests.adults.toString()
      : "") +
    (formData.guests.children
      ? "&children=" + formData.guests.children.toString()
      : "") +
    (formData.guests.infants
      ? "&infants=" + formData.guests.infants.toString()
      : "") +
    (formData.guests.pets ? "&pets=" + formData.guests.pets.toString() : "") +
    "&source=structured_search_input_header" +
    "&search_type=filter_change" +
    "&search_mode=regular_search" +
    (formData.priceMin ? "&price_min=" + formData.priceMin.toString() : "") +
    (formData.priceMax ? "&price_max=" + formData.priceMax.toString() : "") +
    "&min_bedrooms=" +
    formData.bedrooms.toString() +
    "&min_bathrooms=" +
    formData.bathrooms.toString() +
    (formData.amenities.includes("Wifi") ? "&amenities%5B%5D=4" : "") +
    (formData.amenities.includes("Kitchen") ? "&amenities%5B%5D=8" : "") +
    (formData.amenities.includes("Washer") ? "&amenities%5B%5D=33" : "") +
    (formData.amenities.includes("Dryer") ? "&amenities%5B%5D=34" : "") +
    (formData.amenities.includes("Free Parking") ? "&amenities%5B%5D=9" : "") +
    (formData.amenities.includes("Gym") ? "&amenities%5B%5D=15" : "") +
    (formData.amenities.includes("Pool") ? "&amenities%5B%5D=7" : "") +
    (formData.guests.pets ? "&selected_filter_order%5B%5D=pets%3A1" : "");

  console.log(url);

  const result = JSON.stringify({
    url: url,
    user_pref: formData,
  });

  return result;
};

const PageContainer = styled(Box)({
  width: '100%', // Full viewport width
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  flexDirection: 'column',
  margin: 0,
  padding: 0,
  gap: '20px',
});

const SearchContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'flex-start', // Align to the left
  backgroundColor: '#ffffff',
  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
  borderRadius: '40px',
  width: '100%',
  padding: '8px',
  [theme.breakpoints.down('md')]: {
    flexDirection: 'column',
    borderRadius: '20px',
  },
}));

const SearchField = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'flex-start',
  flex: 1,
  padding: '8px 16px',
  flexDirection: 'column',
  borderRight: '1px solid #ddd',
  marginRight: '8px', 
  '&:last-child': {
    marginRight: '0', 
  },
  [theme.breakpoints.down('md')]: {
    borderRight: 'none',
    width: '100%',
    marginRight: '0',
  },
}));

const SearchInput = styled(InputBase)({
  flex: 1,
  fontSize: '14px',
});

const SearchInputField = ({ label, name, id, value, onChange, ...props }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {label && <label htmlFor={id}>{label}</label>} 
      <SearchInput
        id={id}
        name={name}
        value={value}
        onChange={onChange}
        {...props}
      />
    </div>
  );
};

// const SearchButton = styled(Button)({
//   minWidth: '50px',
//   height: '50px',
//   borderRadius: '50%',
//   backgroundColor: '#FF385C',
//   color: 'white',
//   '&:hover': {
//     backgroundColor: '#E21D4F',
//   },
//   marginLeft: '8px',
// });

const Form = () => {
  const navigate = useNavigate();
  const [formValues, setFormValues] = useState({
    location: "",
    checkIn: "",
    checkOut: "",
    guests: {
      adults: 1,
      children: 0,
      infants: 0,
      pets: 0,
    },
    priceMin: "",
    priceMax: "",
    bedrooms: 1,
    bathrooms: 1,
    additionalInfo: "",
    amenities: [],
  });

  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const query = formatSearchQuery(formValues);
    setIsLoading(true);
    setError(null);
    const data = {"sorted_listings": ["https://airbnb.com/s/San-Diego", "https://airbnb.com/s/San-Francisco", "https://airbnb.com/s/San-Diego", "https://airbnb.com/s/San-Francisco", "https://airbnb.com/s/San-Diego", "https://airbnb.com/s/San-Francisco"]}
    if (Array.isArray(data.sorted_listings)) {
      // Navigate to results page with the URLs
      navigate('/results', { state: { urls: data.sorted_listings } });
    } else {
      setError("Invalid response format from server");
    }

    try {
      const response = await fetch("http://127.0.0.1:5001/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error("Search request failed");
      }

      // const data = await response.json();
      // const data = {"sorted_listings": ["https://airbnb.com/s/San-Diego", "https://airbnb.com/s/San-Francisco", "https://airbnb.com/s/San-Diego", "https://airbnb.com/s/San-Francisco", "https://airbnb.com/s/San-Diego", "https://airbnb.com/s/San-Francisco"]}
      // if (Array.isArray(data.sorted_listings)) {
      //   // Navigate to results page with the URLs
      //   navigate('/results', { state: { urls: data.sorted_listings } });
      // } else {
      //   setError("Invalid response format from server");
      // }
    } catch (error) {
      console.error("Error during search:", error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <PageContainer >
        <SearchContainer>
          <SearchField>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>Where</Typography>
            <SearchInputField id="location" name="location" type="text" placeholder="Search destinations" value={formValues.location} onChange={handleChange} />
          </SearchField>

          <SearchField>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>Check in</Typography>
            <SearchInputField id="checkin" name="checkIn" type="date" placeholder="Add dates" value={formValues.checkIn} onChange={handleChange} />
          </SearchField>

          <SearchField  sx={{ borderRight: 'none'}}>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>Check out</Typography>
            <SearchInputField id="checkout" name="checkOut" type="date" placeholder="Add dates" value={formValues.checkOut} onChange={handleChange} />
          </SearchField>
        </SearchContainer>
        <TextField
          id="additionalInfo"
          name="additionalInfo"
          type="text"
          placeholder="I want a..."
          value={formValues.additionalInfo}
          onChange={handleChange}
          multiline
          rows={8}
          sx={{
            width: '80vw',   
            boxSizing: 'border-box',
          }}
        />
        <Button
          type="submit"
          variant="contained"
          disabled={isLoading}
          sx={{
            padding: "12px 24px",
            fontSize: "1rem",
            fontWeight: "bold",
            fontFamily: '"Circular", sans-serif',
            borderRadius: "8px",
            backgroundColor: isLoading ? "#ff8a8c" : "#FF5A5F",
            color: "#ffffff",
            position: "relative",
            transition: "all 0.3s ease",
            "&:hover": {
              backgroundColor: "#FF3B39",
            },
            "&:disabled": {
              backgroundColor: "#ff8a8c",
              color: "#ffffff",
            }
          }}
        >
          {isLoading ? (
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center',
              gap: 1
            }}>
              <span className="loading-dots">Searching</span>
              <Box sx={{
                display: 'inline-flex',
                gap: '4px',
                alignItems: 'center',
                '& .dot': {
                  width: '4px',
                  height: '4px',
                  backgroundColor: '#ffffff',
                  borderRadius: '50%',
                  animation: 'bounce 1.4s infinite ease-in-out both',
                  '&:nth-of-type(1)': {
                    animationDelay: '-0.32s'
                  },
                  '&:nth-of-type(2)': {
                    animationDelay: '-0.16s'
                  },
                  '@keyframes bounce': {
                    '0%, 80%, 100%': {
                      transform: 'scale(0)'
                    },
                    '40%': {
                      transform: 'scale(1)'
                    }
                  }
                }
              }}>
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </Box>
            </Box>
          ) : (
            "Search"
          )}
        </Button>
      </PageContainer>
    </form>
  );
};


export default Form;

