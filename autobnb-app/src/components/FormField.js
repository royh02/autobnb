import React from "react";
import { TextField } from "@mui/material";

const FormField = ({ label, name, id, value, onChange, ...props }) => {
  return (
    <TextField
      id={id}
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
