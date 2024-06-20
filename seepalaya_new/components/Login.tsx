"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import { useFormik } from "formik";
import * as Yup from "yup";
import axios from "axios";
import { Eye, EyeOff } from "lucide-react";

const Login = () => {
  const router = useRouter();
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    const isAuthenticated = localStorage.getItem("user-auth") ? true : false;
    if (isAuthenticated) {
      router.push("/dashboard");
    }
  });
  useEffect(() => {
    setRememberMe(localStorage.getItem("rememberme") ? true : false);
  }, []);

  const formik = useFormik({
    initialValues: {
      username: "",
      password: "",
    },
    validationSchema: Yup.object({
      username: Yup.string()
        .required("Username or email is required")
        .matches(/^[^\s<>'"%;|&]+$/, "Username contains restricted characters"),
      password: Yup.string()
        .required("Password is required")
        .matches(/^[^\s<>'"%;|&]+$/, "Password contains restricted characters"),
    }),
    onSubmit: async (values, { setSubmitting, setErrors, setStatus }) => {
      try {
        const response = await axios.post(
          `${process.env.NEXT_PUBLIC_LOGIN_URL}`,
          {
            username_or_email: values.username,
            password: values.password,
          },
          {
            withCredentials: true,
          }
        );
        const isSuccess = await response.data.success;
        const { full_name, access_token, user_type } = await response.data.data;
        if (isSuccess) {
          localStorage.setItem("user-auth", access_token);
          localStorage.setItem("user", full_name);
          const userIsTeacher: boolean = user_type.includes("teacher");
          localStorage.setItem("isTeacher", userIsTeacher.toString());
          if (rememberMe) {
            localStorage.setItem("uname", values.username);
            localStorage.setItem("upass", values.password);
            localStorage.setItem("rememberme", "remembered");
          } else {
            localStorage.setItem("uname", "");
            localStorage.setItem("upass", "");
            localStorage.setItem("rememberme", "");
          }
          router.push("/dashboard");
        } else {
          setErrors({ password: "Invalid credentials, please try again." });
        }
      } catch (error) {
        let backendError = "Encountered an error!. Please try again later.";
        if (axios.isAxiosError(error)) {
          if (error.response?.data?.detail) {
            backendError = error.response?.data?.detail;
          } else {
            backendError = error.response?.data?.message;
          }
        }
        setStatus(backendError);
      } finally {
        setSubmitting(false);
      }
    },
  });
  useEffect(() => {
    formik.setValues({
      username: localStorage.getItem("uname") || "",
      password: localStorage.getItem("upass") || "",
    });
  }, []);
  const handleRememberMe = () => {
    setRememberMe(!rememberMe);
  };
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <section className="w-[90%] mx-auto max-w-7xl mt-20">
      <div className="flex flex-col ">
        <h2 className="text-3xl font-semibold text-secondary">Log in</h2>
        <div className="flex flex-col">
          <form
            onSubmit={formik.handleSubmit}
            className="w-[100%] max-w-lg  rounded"
          >
            <div className="my-7 ">
              <div className="flex flex-col gap-1">
                <label htmlFor="username">Your Email or username</label>
                <input
                  type="text"
                  name="username"
                  placeholder="Enter your email or username"
                  className="border-b-2 focus:border focus:pl-2 w-[100%] py-2 outline-none"
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  value={formik.values.username}
                />
              </div>
              {formik.touched.username && formik.errors.username ? (
                <div className="text-red-500 mt-1 text-sm">
                  {formik.errors.username}
                </div>
              ) : null}
            </div>
            <div className="my-7">
              <div className="flex flex-col">
                <label htmlFor="password">Your Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    placeholder="Enter your password"
                    className="border-b-2 focus:border focus:pl-2 w-[100%] py-2 outline-none pr-10"
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.password}
                    autoComplete="true"
                  />
                  <div
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 cursor-pointer"
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
            <div className="my-2 text-center">
              <button
                type="submit"
                className=" bg-quarternary hover:bg-quarternary px-5 py-2 rounded-[25px] text-tertiary text-2xl"
                disabled={
                  formik.isSubmitting ||
                  !!formik.errors.username ||
                  !!formik.errors.password
                }
              >
                {formik.isSubmitting ? "Logging in..." : "Log in"}
              </button>
            </div>
            <div className="my-7">
              <div className="flex gap-2">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={handleRememberMe}
                />
                <span
                  className="font-semibold cursor-pointer"
                  onClick={handleRememberMe}
                >
                  Remember me
                </span>
              </div>
            </div>
            <div className="flex justify-start my-7 text-info">
              <Link href="/account/forgot-password" className="mr-2 underline">
                Forgot Password?
              </Link>
            </div>

            {formik.status && (
              <div className="text-red-500 text-center mt-4 text-sm">
                {formik.status}
              </div>
            )}
            <div className="my-4">
              <div className="text-center text-secondary flex justify-between text-sm">
                Dont have an account?
                <span>
                  <Link className="text-infohover" href="/account/choose-role">
                    Create an account
                  </Link>
                </span>
              </div>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
};

export default Login;
