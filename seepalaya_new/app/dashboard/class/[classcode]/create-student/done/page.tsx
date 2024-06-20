"use client";
import { useRouter, useParams } from "next/navigation";
import React, { useEffect, useState } from "react";
import { ArrowLeft } from "lucide-react";

interface StudentData {
  classTitle: string;
  studentsCount: number;
  file_url: string;
  students: Array<{ fullname: string; password: string; username: string }>;
}

const StudentCreationCompletePage = () => {
  const router = useRouter();
  const params = useParams();
  const classcode = Array.isArray(params.classcode)
    ? params.classcode[0]
    : params.classcode;

  const [data, setData] = useState<StudentData | null>(null);

  useEffect(() => {
    const storedData = localStorage.getItem("studentCreationResponse");
    if (storedData) {
      setData(JSON.parse(storedData));
    }
  }, []);

  if (!data) {
    return <div className="loader"></div>;
  }

  return (
    <div className="p-4 text-center">
      <div className="flex items-center">
        <button
          className="px-2 py-2 border border-black ml-2 rounded z-10"
          onClick={() => router.push("/dashboard/class")}
        >
          <ArrowLeft />
        </button>
        <div className="font-bold text-xl text-center flex-1 -ml-8">
          Create class
        </div>
      </div>
      <div className="flex flex-col mt-20">
        <h2 className="text-md mb-3 ">Success!</h2>
        <h3 className="text-md">Created class</h3>
        <p className="text-2xl font-semibold capitalize">{data?.classTitle}</p>
        <p className="text-lg">that has</p>
        <p className="text-2xl font-bold">{data?.studentsCount} students</p>
        <div className="mt-6">
          <p>Download class list as a CSV file</p>
          <p className="text-sm text-gray-500 mt-2 mx-2">
            [Note: once you have left this screen, you cannot download the file
            later]
          </p>
          <div className="mt-12">
            <a
              href={`${process.env.NEXT_PUBLIC_BASE_URL}/${data?.file_url}`}
              download
              className="bg-reddish text-white py-5 px-8 rounded-3xl font-bold text-2xl"
            >
              Download CSV
            </a>
          </div>
          <div className="mt-8">
            <button
              onClick={() => router.push(`/dashboard/class/${classcode}/classview`)}
              className="bg-reddish text-white py-3 px-5 rounded-3xl font-bold text-2xl"
            >
              Go to class
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentCreationCompletePage;
