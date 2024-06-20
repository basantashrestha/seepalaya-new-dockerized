"use client";
import { useRouter } from "next/navigation";
import React, { useState } from "react";
import { useFormik } from "formik";
import * as Yup from "yup";
import axios from "axios";
import { Eye, EyeOff } from "lucide-react";

const SignUpProfile = () => {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const formik = useFormik({
    initialValues: {
      fullname: "",
      email: "",
      password: "",
      confirm_password: "",
    },
    validationSchema: Yup.object({
      fullname: Yup.string()
        .required("Fullname is required")
        .matches(/^[^<>'"%;|&]+$/, "fullname contains restricted characters"),
      email: Yup.string()
        .required("Email is required")
        .matches(/^[^\s<>'"%;|&]+$/, "email contains restricted characters"),
      password: Yup.string()
        .required("Password is required")
        .matches(/^[^\s<>'"%;|&]+$/, "Password contains restricted characters"),
      confirm_password: Yup.string()
        .required("Confirm Password is required")
        .oneOf([Yup.ref("password")], "Passwords must match")
        .matches(
          /^[^\s<>'"%;|&]+$/,
          "Confirm Password contains restricted characters"
        ),
    }),
    onSubmit: async (values, { setSubmitting, setErrors, setStatus }) => {
      try {
        const response = await axios.post(
          `${process.env.NEXT_PUBLIC_TEACHER_SIGNUP_URL}`,

          {
            full_name: values.fullname,
            email: values.email,
            password: values.password,
            confirm_password: values.confirm_password,
          }
        );
        const isSuccess = response.data.success;
        if (isSuccess) {
          const { access_token, full_name, user_type } = response.data.data;
          localStorage.setItem("user-auth", access_token);
          localStorage.setItem("user", full_name);
          const userIsTeacher: boolean = user_type.includes("teacher");
          localStorage.setItem("isTeacher", userIsTeacher.toString());

          localStorage.setItem("uname", "");
          localStorage.setItem("upass", "");
          localStorage.setItem("rememberme", "");
          router.push("/dashboard");
        } else {
          setErrors({ password: "Invalid credentials, please try again." });
        }
      } catch (error) {
        let backendError =
          "An error occurred during signup. Please try again later.";
        if (axios.isAxiosError(error)) {
          backendError = error.response?.data?.message || backendError;
        }
        setStatus(backendError);
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
    <section className="w-[90%] mx-auto max-w-7xl mt-20">
      <div className="flex flex-col">
        <h2 className="text-3xl font-semibold  text-secondary max-w-xl ">
          Sign Up to Seepalaya
        </h2>
        <div className="flex flex-col">
          <form onSubmit={formik.handleSubmit} className="">
            <div className="my-7 ">
              <div className="flex flex-col gap-1">
                <label htmlFor="fullname">Your name</label>
                <input
                  type="text"
                  name="fullname"
                  placeholder="Enter your name"
                  className="border-b-2 focus:border focus:pl-2 w-[100%] py-2 outline-none"
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  value={formik.values.fullname}
                />
              </div>
              {formik.touched.fullname && formik.errors.fullname ? (
                <div className="text-red-500 mt-1 text-sm">
                  {formik.errors.fullname}
                </div>
              ) : null}
            </div>
            <div className="my-7 ">
              <div className="flex flex-col gap-1">
                <label htmlFor="email">Your email</label>
                <input
                  type="text"
                  name="email"
                  placeholder="Enter your email"
                  className="border-b-2 focus:border focus:pl-2 w-[100%] py-2 outline-none"
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  value={formik.values.email}
                />
              </div>
              {formik.touched.email && formik.errors.email ? (
                <div className="text-red-500 mt-1 text-sm">
                  {formik.errors.email}
                </div>
              ) : null}
            </div>
            <div className="my-7 ">
              <div className="flex flex-col gap-1">
                <label htmlFor="password">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    placeholder="Enter your password"
                    className="border-b-2 focus:border focus:pl-2 w-[100%] py-2 outline-none"
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.password}
                    autoComplete="false"
                  />
                  <div
                    className="absolute right-2 top-1/2 transform -translate-y-1/2"
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
            <div className="my-7 ">
              <div className="flex flex-col gap-1">
                <label htmlFor="confirm_password">Confirm Password</label>
                <div className="relative">
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    name="confirm_password"
                    placeholder="Enter your password again"
                    className="border-b-2 focus:border focus:pl-2 w-[100%] py-2 outline-none"
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.confirm_password}
                    autoComplete="false"
                  />
                  <div
                    className="absolute right-2 top-1/2 tranform -translate-y-1/2"
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

            <div className="my-2 text-center">
              <button
                type="submit"
                className=" bg-quarternary hover:bg-quarternary px-5 py-2 rounded-[25px] text-tertiary text-2xl"
                disabled={
                  formik.isSubmitting ||
                  !!formik.errors.email ||
                  !!formik.errors.password
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

export default SignUpProfile;
