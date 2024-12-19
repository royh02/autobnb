import React, { useState } from 'react';
import {TextField, Typography, Box } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

const Key = () => {
  const [apiKey, setApiKey] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!apiKey) {
      setError('Please enter a valid API key');
    } else {
      setError('');
      console.log('API Key Submitted:', apiKey);
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '16px',
        width: '100%',
        maxWidth: '400px',
        margin: '10px',
        padding: '16px',
        borderRadius: '8px',
        // boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
        backgroundColor: '#fff',
      }}
    >
      <form onSubmit={handleSubmit} style={{ width: '100%', flexDirection: 'row' }}>
        <Box sx={{ display: 'flex', gap: '8px', width: '100%' }}>
            <TextField
                label="API Key"
                variant="outlined"
                fullWidth
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                error={!!error}
                helperText={error}
                sx={{
                    marginBottom: '16px',
                }}
                />
        </Box>
      </form>
    </Box>
  );
};

export default Key;
