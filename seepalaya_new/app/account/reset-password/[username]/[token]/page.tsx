"use client";
import { useRouter } from "next/navigation";
import React, { useState } from "react";
import { useFormik } from "formik";
import * as Yup from "yup";
import axios from "axios";
import { Eye, EyeOff } from "lucide-react";

const ResetPassword = ({ params }: any) => {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const { username, token } = params;

  const formik = useFormik({
    initialValues: {
      password: "",
      confirm_password: "",
    },
    validationSchema: Yup.object({
      password: Yup.string()
        .required("Password is required")
        .matches(/^[^\s<>'"%;|&]+$/, "Password contains restricted characters"),
      confirm_password: Yup.string()
        .required("Confirm password is required")
        .oneOf([Yup.ref("password")], "Passwords must match")
        .matches(
          /^[^\s<>'"%;|&]+$/,
          "Confirm password contains restricted characters"
        ),
    }),
    onSubmit: async (values, { setSubmitting, setErrors, setStatus }) => {
      try {
        const response = await axios.post(
          `${process.env.NEXT_PUBLIC_RESET_URL}`,
          {
            username,
            token,
            password: values.password,
            confirm_password: values.password,
          }
        );
        const isSuccess = response.data.success;
        if (isSuccess) {
          router.push("/account/login");
        } else {
          setErrors({ password: "Invalid credentials, please try again." });
        }
      } catch (error) {
        setStatus("An error occurred during login. Please try again later.");
      } finally {
        setSubmitting(false);
      }
    },
  });

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };
  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };
  return (
    <section className="mt-20">
      <div className="flex flex-col w-[90%] mx-auto max-w-7xl">
        <h3 className="text-2xl font-semibold text-secondary ">
          Change your password
        </h3>
        <div className="flex flex-col">
          <form onSubmit={formik.handleSubmit} className="w-[100%]  max-w-lg">
            <div className="my-7">
              <div className="flex flex-col">
                <label htmlFor="password">New Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    placeholder="Type in your new password"
                    className="border-b-2 focus:border focus:pl-2 w-[100%]  py-2 outline-none"
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.password}
                    autoComplete="false"
                  />
                  <div
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 "
                    onClick={togglePasswordVisibility}
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </div>
                </div>
              </div>
              {formik.touched.password && formik.errors.password ? (
                <div className="text-red-500 mt-1 text-sm">
                  {formik.errors.password}
                </div>
              ) : null}
            </div>
            <div className="my-7">
              <div className="flex flex-col">
                <label htmlFor="confirm_password">Confirm Password</label>
                <div className="relative">
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    name="confirm_password"
                    placeholder="Type in to confirm"
                    className="border-b-2 focus:border focus:pl-2 w-[100%]  py-2 outline-none"
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.confirm_password}
                    autoComplete="false"
                  />
                  <div
                    className="absolute right-2 top-1/2 transform -translate-y-1/2"
                    onClick={toggleConfirmPasswordVisibility}
                  >
                    {showConfirmPassword ? (
                      <EyeOff size={20} />
                    ) : (
                      <Eye size={20} />
                    )}
                  </div>
                </div>
              </div>
              {formik.touched.confirm_password &&
              formik.errors.confirm_password ? (
                <div className="text-red-500 mt-1 text-sm">
                  {formik.errors.confirm_password}
                </div>
              ) : null}
            </div>

            <div className="my-2 flex justify-center">
              <button
                type="submit"
                className="bg-quarternary hover:bg-quarternary py-2 px-4 rounded-lg text-white"
                disabled={
                  formik.isSubmitting ||
                  !!formik.errors.password ||
                  !!formik.errors.confirm_password
                }
              >
                {formik.isSubmitting ? "Submitting..." : "Submit"}
              </button>
            </div>
            {formik.status && (
              <div className="text-red-500 text-center mt-4">
                {formik.status}
              </div>
            )}
          </form>
        </div>
      </div>
    </section>
  );
};

export default ResetPassword;
