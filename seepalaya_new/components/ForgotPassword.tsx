"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import React from "react";
import { useFormik } from "formik";
import * as Yup from "yup";
import axios from "axios";
import { ArrowLeft } from "lucide-react";

const Login = () => {
  const router = useRouter();

  const formik = useFormik({
    initialValues: {
      email: "",
    },
    validationSchema: Yup.object({
      email: Yup.string()
        .required("Email is required")
        .matches(/^[^\s<>'"%;|&]+$/, "Email contains restricted characters"),
    }),
    onSubmit: async (values, { setSubmitting, setErrors, setStatus }) => {
      try {
        const response = await axios.post(
          `${process.env.NEXT_PUBLIC_FORGOT_PASSWORD_URL}`,
          {
            email: values.email,
          }
        );
        const isSuccess = await response.data.success;
        if (isSuccess) {
          router.push('/account/forgot-password/done');
        } else {
          setErrors({ email: "Invalid email, please try again." });
        }
      } catch (error) {
        let backendError = "Encountered an error!. Please try again later.";
        if(axios.isAxiosError(error)){
          backendError = error.response?.data?.message;
        }
        setStatus(backendError);
      } finally {
        setSubmitting(false);
      }
    },
  });

  return (
    <>
      <section className="mt-20 w-[90%] mx-auto max-w-7xl">
        <button
          className="px-2 py-2 bg-grayish  rounded cursor-pointer"
          onClick={() => router.push("/account/login")}
        >
          <ArrowLeft />
        </button>
        <div className="flex flex-col ">
          <div className="flex flex-col">
            <form
              onSubmit={formik.handleSubmit}
              className="w-[100%] max-w-lg py-4"
            >
              <div className="my-7 ">
                <div className="flex flex-col gap-1">
                  <label htmlFor="email">Your Email</label>
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

              <div className=" my-4 flex justify-center">
                <button
                  type="submit"
                  className="bg-quarternary hover:bg-quarternary py-2 px-4 rounded-lg text-white text-center"
                >
                  {formik.isSubmitting ? "Sending Email..." : "Send Email"}
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
    </>
  );
};

export default Login;
