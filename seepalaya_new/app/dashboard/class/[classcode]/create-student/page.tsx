"use client";

import { useRouter, useParams } from "next/navigation";
import React, { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { RootState, AppDispatch } from "@/lib/redux/store";
import { fetchClassDetails } from "@/lib/redux/features/classroom/classDetailSlice";
import { ArrowLeft, Users } from "lucide-react";
import { createStudentData } from "@/lib/redux/features/classroom/createStudentSlice";
import Papa from "papaparse";
import Modal from "@/components/Modal";
import Loading from "@/components/Loading";
import Link from "next/link";

const CreateStudent = () => {
  const router = useRouter();
  const params = useParams();
  const dispatch = useDispatch<AppDispatch>();

  const { loading, error, data, status } = useSelector(
    (state: RootState) => state.classDetails
  );
  useEffect(() => {
    if (status === 401) {
      return router.push("/account/login");
    }
  }, []);
  const { loading: studentCreationLoading, error: studentCreationError } =
    useSelector((state: RootState) => state.createStudent);

  const [students, setStudents] = useState([{ name: "" }]);
  const [formError, setFormError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const classcode = Array.isArray(params.classcode)
    ? params.classcode[0]
    : params.classcode;

  useEffect(() => {
    if (classcode) {
      dispatch(fetchClassDetails(classcode));
    }
  }, [dispatch, classcode]);

  const addRow = () => {
    if (students.length <= 100) {
      setStudents([...students, { name: "" }]);
    }
  };

  const addFiveRows = () => {
    if (students.length + 5 <= 100) {
      setStudents([...students, ...Array(5).fill({ name: "" })]);
    } else if (students.length < 100) {
      setStudents([
        ...students,
        ...Array(100 - students.length).fill({ name: "" }),
      ]);
    }
  };

  const handleInputChange = (
    index: number,
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const values = [...students];
    values[index].name = event.target.value;
    setStudents(values);
  };

  const handleRemoveRow = (index: number) => {
    const values = [...students];
    values.splice(index, 1);
    setStudents(values);
    if (values.length === 0) {
      setFormError(null);
    }
  };

  const handleFileSelect = (file: File) => {
    Papa.parse(file, {
      complete: (results) => {
        const data = results.data as string[][];
        const csvStudents = data.map((row) => ({
          name: row[0],
        }));
        const newStudents = [...students, ...csvStudents].slice(0, 100);
        setStudents(newStudents);
      },
      header: false,
    });
    setIsModalOpen(false);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const filteredStudents = students.filter(
      (student) => student.name.trim() !== ""
    );

    if (filteredStudents.length === 0) {
      setFormError("Please add at least one student name.");
      return;
    }

    setFormError(null);
    try {
      const studentsName = filteredStudents.map((student) => student.name);
      const res = await dispatch(
        createStudentData({ students: studentsName, class_code: classcode })
      ).unwrap();
      if (res.success) {
        return router.push(`/dashboard/class/${classcode}/create-student/done`);
      }
    } catch (error) {
      // Handle error if needed
    }
  };

  if (loading || studentCreationLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Loading />
      </div>
    );
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <>
      <div className=" bg-grayish py-2">
        <div className="flex items-center">
          <button
            className="px-2 py-2 border border-black ml-2 rounded cursor-pointer z-10"
            onClick={() => router.push("/dashboard/class")}
          >
            <ArrowLeft />
          </button>
          <div className="font-bold text-xl text-center flex-1 -ml-8">
            Create class
          </div>
        </div>
        <div className="bg-gray-200 p-4 rounded-md">
          <h2 className="text-2xl font-bold capitalize text-center">
            {data?.title}
          </h2>
          <div className="flex justify-between mt-2">
            <p className="text-md text-center font-semibold">{`Class code: ${classcode}`}</p>
            <div className="text-md text-center flex items-center gap-2">
              <Users />
              <p>
                <span className="font-semibold mr-1">
                  {data?.studentsCount}
                </span>
                students
              </p>
            </div>
          </div>
        </div>
      </div>
      <section className="mt-4 w-[90%] mx-auto max-w-7xl">
        <form className="mt-4" onSubmit={handleSubmit}>
          {students.map((student, index) => (
            <div key={index} className="flex items-center mb-2">
              <input
                type="text"
                placeholder="Enter student name"
                value={student.name}
                onChange={(e) => handleInputChange(index, e)}
                className="flex-1 border p-2 rounded-md"
              />
              <button
                type="button"
                onClick={() => handleRemoveRow(index)}
                className="ml-2 text-red-500 text-3xl"
              >
                &times;
              </button>
            </div>
          ))}
          {formError && (
            <p className="text-red-500 text-center my-2">{formError}</p>
          )}
          <div className="text-center">
            <button
              type="button"
              onClick={addRow}
              className={`block text-red-500 my-2 ${
                students.length > 100 ? "cursor-unset opacity-50" : ""
              }`}
              disabled={students.length > 100}
            >
              + add row
            </button>
            <button
              type="button"
              onClick={addFiveRows}
              className={`block text-red-500 my-2 ${
                students.length > 100 ? "cursor-unset opacity-50" : ""
              }`}
              disabled={students.length > 100}
            >
              + add 5 more rows
            </button>
            <button
              type="button"
              onClick={() => setIsModalOpen(true)}
              className="block text-red-500 my-2 cursor-pointer"
            >
              + import CSV
            </button>
            <button
              type="submit"
              className="bg-red-500 text-white py-2 px-4 rounded-lg my-4"
            >
              Create student
            </button>
            {studentCreationError && (
              <div className="text-center mt-4 text-red-500">
                {studentCreationError}
              </div>
            )}
            <Link
              className="text-reddish flex justify-end mr-3 text-xl"
              href={`/dashboard/class/${classcode}/classview`}
            >
              Skip
            </Link>
          </div>
        </form>
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onFileSelect={handleFileSelect}
        />
      </section>
    </>
  );
};

export default CreateStudent;
