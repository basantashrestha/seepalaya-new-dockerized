"use client";
import { Check, Edit, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchClassDetails } from "@/lib/redux/features/classroom/classDetailSlice";
import { AppDispatch, RootState } from "@/lib/redux/store";
import { useRouter } from "next/navigation";
import { updateClassInfoData } from "@/lib/redux/features/classroom/updateClassInfoSlice";

const ClassViewClassDetails = ({ classcode }: any) => {
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState("");
  const dispatch = useDispatch<AppDispatch>();
  const router = useRouter();
  useEffect(() => {
    dispatch(fetchClassDetails(classcode));
  }, []);
  const { data, loading, status } = useSelector(
    (state: RootState) => state.classDetails
  );
  useEffect(() => {
    if (status === 401) {
      return router.push("/account/login");
    }
  }, []);
  useEffect(() => {
    if (data) {
      setTitle(data.title);
    }
  }, [data]);

  const handleEditToggle = async() => {
    if (isEditing) {
      const response = await dispatch(updateClassInfoData({ title, class_code: classcode }));
      if(updateClassInfoData.fulfilled.match(response) && response.payload.success){
        
      }else{
        //handle error
      }
    }
    setIsEditing(!isEditing);
  };

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTitle(e.target.value);
  };
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="loader"></div>
      </div>
    );
  }
  return (
    <section className="bg-gray-100 p-5 rounded-lg mb-5">
      <div className="flex justify-between items-center mb-3">
        {isEditing ? (
          <input
            type="text"
            value={title}
            onChange={(e) => handleTitleChange(e)}
            className="text-xl font-bold capitalize p-2 border rounded"
          />
        ) : (
          <h2 className="text-xl font-bold capitalize">{title}</h2>
        )}
        <button className="p-2" onClick={handleEditToggle}>
          {isEditing ? <Check size={20} /> : <Edit size={20} />}
        </button>
      </div>
      <p>
        Class ID <span className="font-bold">{classcode}</span>
      </p>
      <div className="flex items-center mt-3">
        <Users className="mr-2" /> {data?.studentsCount} students
      </div>
      <div className="mt-5">
        <p>Recent activity:</p>
        <p className="mt-2 flex items-center">
          <span className="mr-2">📚</span>Course: Global warming and climate
          change this could also be much longer
        </p>
        <p className="mt-2 flex items-center">
          <span className="mr-2">📝</span>Quiz: Dinosaurs of the Cretaceous same
          thing also applies here
        </p>
      </div>
    </section>
  );
};

export default ClassViewClassDetails;
