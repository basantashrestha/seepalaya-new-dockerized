'use client';
import { useRouter } from "next/navigation";
import React from "react";

const Button = ({label,routePath}:any) => {
    const router = useRouter();
  return (
    <button
      className="bg-quarternary hover:bg-quarternary text-tertiary px-5 py-3 rounded-lg"
      onClick={() =>router.push(routePath)}
    >
      {label}
    </button>
  );
};

export default Button;
