"use client";
import { ArrowLeft } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import ClassViewClassDetails from "@/components/ClassViewClassDetails";
import ClassViewStudentDetails from "@/components/ClassViewStudentDetails";
import { useEffect, useState } from "react";
import ErrorPage from "@/components/ErrorPage";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "@/lib/redux/store";
import { fetchStudents } from "@/lib/redux/features/classroom/listStudentsSlice";

const ClassView = () => {
  const [accessGranted, setAccessGranted] = useState(false);
  const router = useRouter();
  const dispatch = useDispatch<AppDispatch>();

  const { classcode } = useParams<{ classcode: string }>();
  const { status, data } = useSelector(
    (state: RootState) => state.listStudents
  );
  useEffect(() => {
    dispatch(fetchStudents(classcode));
  }, [classcode]);
  useEffect(() => {
    if (data) {
      setAccessGranted(true);
    }
  }, [data]);
  if (status === 403 || status === 400) {
    return <ErrorPage />;
  }

  return (
    <div className="p-5">
      <header className="flex items-center mb-5">
        <button
          className="mr-3 p-2 border border-black rounded cursor-pointer"
          onClick={() => router.push("/dashboard/class")}
        >
          <ArrowLeft />
        </button>
        <h1 className="text-2xl font-bold">Class view</h1>
      </header>

      {accessGranted && <ClassViewClassDetails classcode={classcode} />}
      {accessGranted && <ClassViewStudentDetails classcode={classcode} />}
    </div>
  );
};

export default ClassView;
