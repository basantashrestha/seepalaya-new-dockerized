"use client";
import { FC, useEffect } from "react";
import { ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "@/lib/redux/store";
import { fetchClasses } from "@/lib/redux/features/classroom/listClassesSlice";
import Loading from "@/components/Loading";

const ManageClasses: FC = () => {
  const router = useRouter();
  const dispatch = useDispatch<AppDispatch>();
  useEffect(() => {
    dispatch(fetchClasses());
  }, []);
  const { data: classesData, loading } = useSelector(
    (state: RootState) => state.listClasses
  );
  console.log(classesData);
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Loading />
      </div>
    );
  }
  return (
    <div className="p-4">
      <div className="flex items-center mb-4">
        <button className="p-2">
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-lg font-semibold ml-2">Manage Classes</h1>
      </div>
      <div className="space-y-4">
        {classesData.map((classItem, index) => (
          <div
            key={index}
            className="p-4 border rounded-lg cursor-pointer"
            onClick={() =>
              router.push(
                `/dashboard/class/${classItem.classroom_code}/classview`
              )
            }
          >
            <div className="flex justify-between">
              <h2 className="text-xl font-bold">{classItem.classroom_title}</h2>
            </div>
            <p>Class ID: {classItem.classroom_code}</p>
            <p>{classItem.student_count} students</p>
            <div>
              <p className="font-semibold mt-2">Recent activity:</p>
              <p className="flex items-center">
                <span className="mr-2">
                  "📖"
                </span>
                Course: Global warming and climate change
              </p>
              <p className="flex items-center">
                <span className="mr-2">
                   "📝"
                </span>
                Quiz: Dinosaurs of the Cretaceous
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ManageClasses;
