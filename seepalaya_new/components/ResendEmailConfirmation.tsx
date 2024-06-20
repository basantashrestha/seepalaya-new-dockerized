"use client";
import { useRouter } from "next/navigation";
import React from "react";
import { useFormik } from "formik";
import * as Yup from "yup";
import axios from "axios";

const ResendEmailConfirmation = () => {
  const router = useRouter();
  //   const token = localStorage.getItem('user-auth') || '';

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
          `${process.env.NEXT_PUBLIC_RESEND_EMAIL_CONFIRMATION_URL}`,
          {
            email: values.email,
          }
        );
        const isSuccess = await response.data.success;
        if (isSuccess) {
          router.push("/account/reset-email-confirmation/done");
        } else {
          setErrors({ email: "Invalid email, please try again." });
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

  return (
    <>
      <section className="mt-20 w-[90%] mx-auto max-w-7xl">
        <div className="">
          <p className="text-center text-sm">
            Hey there, it seems your email still needs verification.
          </p>
          <p className="text-center text-sm">
            Enter your email to receive new verification email.
          </p>
        </div>
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

export default ResendEmailConfirmation;
