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

const formatSearchQuery = (formData) => {
  const result = JSON.stringify({
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
    additionalInfo: "",
    key: ""
  });

  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleGenerateQuery = async (e) => {
    e.preventDefault();
    setIsGenerating(true);
    setError(null);
  
    try {
      const response = await fetch("http://127.0.0.1:5001/api/generate_query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });
  
      if (!response.ok) {
        throw new Error("Failed to generate query");
      }
  
      const data = await response.json();
  
      setFormValues((prevFormValues) => ({
        ...prevFormValues,
        additionalInfo: data.example_query.replace(/^"(.+)"$/, '$1'),
      }));
  
    } catch (error) {
      console.error("Error generating query:", error);
      setError("Failed to generate query. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    const query = formatSearchQuery(formValues);
    setIsLoading(true);
    setError(null);
    // const data = [
    //   {
    //     "url": "https://www.airbnb.com/rooms/35949681",
    //     "summary": "This charming Airbnb listing offers an exceptional experience with its modern amenities and thoughtful design. Recent guests have praised its spotless cleanliness and attention to detail. The host maintains excellent communication and has earned a reputation for going above and beyond to ensure guest comfort. The property features stylish furnishings and a well-equipped kitchen, making it perfect for both short and extended stays. The location provides a perfect balance of tranquility and accessibility to local attractions."
    //   },
    //   {
    //     "url": "https://www.airbnb.com/rooms/955858690980318819",
    //     "summary": "Guests consistently rate this property highly for its stunning views and prime location. The space is beautifully decorated with a mix of contemporary and classic elements, creating a warm and inviting atmosphere. Previous visitors have particularly enjoyed the spacious layout and premium amenities. The host is known for providing personalized recommendations for local experiences and maintaining the property to high standards. The outdoor space has been highlighted as a particular highlight, perfect for morning coffee or evening relaxation."
    //   },
    //   {
    //     "url": "https://www.airbnb.com/rooms/1238548906544868515",
    //     "summary": "This unique property stands out for its exceptional interior design and thoughtful touches throughout. Reviews frequently mention the comfortable bedding and well-appointed living spaces. The kitchen has received praise for being fully equipped with high-end appliances. Located in a quiet neighborhood, guests appreciate the peaceful environment while still being close to urban conveniences. The host's attention to detail and quick response time have been consistently noted in positive reviews."
    //   },
    //   {
    //     "url": "https://www.airbnb.com/rooms/940785157628196076",
    //     "summary": "A truly remarkable space that combines comfort with elegance. Past guests have highlighted the property's excellent natural lighting and open floor plan. The bedrooms are described as peaceful retreats with premium mattresses and linens. The bathroom features modern fixtures and luxury toiletries. The host has earned a Superhost status for their exceptional service and maintenance of the property. The location offers easy access to both local attractions and essential amenities."
    //   },
    //   {
    //     "url": "https://www.airbnb.com/rooms/1051753142382397501",
    //     "summary": "This listing has garnered praise for its perfect blend of comfort and sophistication. Guests particularly enjoy the well-maintained outdoor space and modern amenities. The property features high-end finishes throughout, from the custom kitchen to the spa-like bathroom. Reviews consistently mention the exceptional cleanliness and the host's professional yet warm approach. The neighborhood offers a perfect mix of residential charm and convenient access to local highlights."
    //   },
    //   {
    //     "url": "https://www.airbnb.com/rooms/47357567",
    //     "summary": "A standout property that receives consistent five-star reviews for its impeccable presentation and comfort. The space has been thoughtfully designed with both style and functionality in mind. Guests frequently comment on the comfortable furniture and high-quality bedding. The kitchen is well-stocked with everything needed for meal preparation. The host is praised for their attentiveness and the property's immaculate maintenance. The location provides easy access to local attractions while maintaining a peaceful atmosphere."
    //   }
    // ];
    // if (Array.isArray(data)) {
    //   // Navigate to results page with the URLs
    //   navigate('/results', { state: { data } });
    // } else {
    //   setError("Invalid response format from server");
    // }

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

      const data = await response.json();
      // const data = {"sorted_listings": ["https://airbnb.com/s/San-Diego", "https://airbnb.com/s/San-Francisco", "https://airbnb.com/s/San-Diego", "https://airbnb.com/s/San-Francisco", "https://airbnb.com/s/San-Diego", "https://airbnb.com/s/San-Francisco"]}
      if (Array.isArray(data.sorted_listings)) {
        // Navigate to results page with the URLs
        navigate('/results', { state: { urls: data.sorted_listings } });
      } else {
        setError("Invalid response format from server");
      }
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
          fullWidth
          multiline
          rows={4}
          name="additionalInfo"
          label="Additional Information"
          value={formValues.additionalInfo}
          onChange={handleChange}
          sx={{
            backgroundColor: "white",
            borderRadius: "4px",
            '& .MuiOutlinedInput-root': {
              '& fieldset': {
                borderColor: 'rgba(0, 0, 0, 0.23)',
              },
            },
            "& .MuiOutlinedInput-root": {
              "&.Mui-focused fieldset": {
                borderColor: "#FF5A5F",
              },
            },
            "& .MuiInputLabel-root.Mui-focused": {
              color: "#FF5A5F",
            },
          }}
        />
        <Box sx={{ display: 'flex', flexDirection: 'row',  justifyContent: 'center', alignItems: 'center', gap: '20px' }}>
          <TextField
            name="key"
            label="OpenAI API Key"
            value={formValues.key}
            onChange={handleChange}
            sx={{
              "& .MuiOutlinedInput-root": {
                "&.Mui-focused fieldset": {
                  borderColor: "#FF5A5F",
                },
              },
              "& .MuiInputLabel-root.Mui-focused": {
                color: "#FF5A5F",
              },
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
          
          <Button
            type="button"
            variant="contained"
            onClick={handleGenerateQuery}
            disabled={isGenerating}
            sx={{
              padding: "12px 24px",
              fontSize: "1rem",
              fontWeight: "bold",
              fontFamily: '"Circular", sans-serif',
              borderRadius: "8px",
              backgroundColor: isGenerating ? "#ff8a8c" : "#FF5A5F",
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
            {isGenerating ? (
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center',
                gap: 1
              }}>
                <span className="loading-dots">I'm Feeling Lucky!</span>
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
              "I'm Feeling Lucky!"
            )}
          </Button>
        </Box>
      </PageContainer>
    </form>
  );
};


export default Form;
