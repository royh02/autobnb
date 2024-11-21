import React from "react";
import { TextField } from "@mui/material";

const FormField = ({ label, name, value, onChange, ...props }) => {
  return (
    <TextField
      label={label}
      name={name}
      value={value}
      onChange={onChange}
      fullWidth
      variant="outlined"
      {...props}
    />
  );
};

export default FormField;
