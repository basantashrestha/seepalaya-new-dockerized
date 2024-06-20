"use client";
import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import { useFormik } from "formik";
import * as Yup from "yup";
import { ArrowLeft } from "lucide-react";
import { useDispatch } from "react-redux";
import { AppDispatch } from "@/lib/redux/store";
import { fetchClassData } from "@/lib/redux/features/classroom/createClassSlice";

const Classroom = () => {
  const router = useRouter();
  const dispatch = useDispatch<AppDispatch>();
  const [isTeacher, setIsTeacher] = useState(false);
  const [loading, setLoading] = useState(true);


  const formik = useFormik({
    initialValues: {
      classroom: "",
    },
    validationSchema: Yup.object({
      classroom: Yup.string()
        .required("Class name is required")
        .matches(
          /^[^\s<>'"%;|&]+$/,
          "Class name contains restricted characters"
        ),
    }),
    onSubmit: async (values, { setSubmitting, setErrors, setStatus }) => {
      setStatus(null);
      try {
        const response = await dispatch(
          fetchClassData(values.classroom)
        ).unwrap();


        router.push(`/dashboard/class/${response.data.class_code}/create-student`);
      } catch (error: any) {
        setStatus(error);
      } finally {
        setSubmitting(false);
      }
    },
  });

  useEffect(() => {
    setIsTeacher(localStorage.getItem("isTeacher") === "true");
    setLoading(false);
  }, []);

  useEffect(() => {
    if (!loading && !isTeacher) {
      router.push("/dashboard");
    }
  }, [loading, isTeacher, router]);

  return (
    <>
      <div className="flex items-center bg-grayish h-16">
        <button
          className="px-2 py-2 border border-black ml-2 rounded cursor-pointer z-10"
          onClick={() => router.push("/dashboard")}
        >
          <ArrowLeft />
        </button>
        <div className="font-bold text-xl text-center flex-1 -ml-8">
          Create class
        </div>
      </div>
      <section className="mt-20 w-[90%] mx-auto max-w-7xl">
        <div className="flex flex-col ">
          <div className="flex flex-col">
            <form
              onSubmit={formik.handleSubmit}
              className="w-[100%] max-w-lg py-4"
            >
              <div className="my-7 ">
                <div className="flex flex-col gap-1">
                  <label htmlFor="classroom">Enter class name</label>
                  <input
                    type="text"
                    name="classroom"
                    placeholder="Eg. Science Resource for Grade 1"
                    className="border-b-2 focus:border focus:pl-2 w-[100%] py-2 outline-none"
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.classroom}
                  />
                </div>
                {formik.touched.classroom && formik.errors.classroom ? (
                  <div className="text-red-500 mt-1 text-sm">
                    {formik.errors.classroom}
                  </div>
                ) : null}
              </div>

              <div className="my-4 flex justify-center mt-20">
                <button
                  type="submit"
                  className="bg-quarternary hover:bg-quarternary py-2 px-4 rounded-lg text-white text-center"
                >
                  Next
                </button>
              </div>
              {formik.status && (
                <div className="text-red-500 text-center mt-4">
                  {formik.status}
                </div>
              )}
              {/* {classState.message && (
                <div className={`text-center mt-4 ${classState.success ? 'text-green-500' : 'text-red-500'}`}>
                  {classState.message}
                </div>
              )} */}
            </form>
          </div>
        </div>
      </section>
    </>
  );
};

export default Classroom;
