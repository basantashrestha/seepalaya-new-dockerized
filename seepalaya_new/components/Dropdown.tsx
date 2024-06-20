'use client';
import React, { useState } from "react";

const Dropdown = () => {
  const [dropdownValue,setDropdownValue] = useState('en');
  const handleDropdown = (value:any) => {
    setDropdownValue(value);
  }
  return (
    <select value={dropdownValue} className="px-5 py-2 rounded-lg" onChange = {(e) => handleDropdown(e.target.value)}>
      <option value="en">English</option>
      <option value="ne">Nepali</option>
      <option value="mai">Maithili</option>
    </select>
  );
};

export default Dropdown;
