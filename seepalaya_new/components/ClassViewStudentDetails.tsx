"use client";
import { AppDispatch, RootState } from "@/lib/redux/store";
import { ArrowDownUp, Search, Settings, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchStudents } from "@/lib/redux/features/classroom/listStudentsSlice";
import { removeStudentData } from "@/lib/redux/features/classroom/removeStudentSlice";
import { fetchClassDetails } from "@/lib/redux/features/classroom/classDetailSlice";
import { addStudent } from "@/lib/redux/features/classroom/addStudentToClassSlice";
import Loading from "./Loading";
import { fetchClasses } from "@/lib/redux/features/classroom/listClassesSlice";

const ClassViewStudentDetails = ({ classcode }: any) => {
  const router = useRouter();
  const dispatch = useDispatch<AppDispatch>();
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const [showSearch, setShowSearch] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [selectedStudents, setSelectedStudents] = useState<string[]>([]);
  const [showClassModal, setShowClassModal] = useState(false);
  const [selectedClass, setSelectedClass] = useState('');

  useEffect(() => {
    dispatch(fetchStudents(classcode));
  }, []);

  const { data, status } = useSelector(
    (state: RootState) => state.listStudents
  );
  const { success: removeStudentSuccess } = useSelector(
    (state: RootState) => state.removeStudents
  );
  const { loading: listClassesLoading, data: listClassesData } = useSelector(
    (state: RootState) => state.listClasses
  );

  useEffect(() => {
    if (status === 401) {
      return router.push("/dashboard");
    }
  }, [status]);

  const handleSortingOrder = () => {
    setSortOrder((prevOrder) => (prevOrder === "asc" ? "desc" : "asc"));
  };

  const filteredData = data?.filter((student) =>
    student.full_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const sortedData = filteredData?.slice().sort((a, b) => {
    if (sortOrder === "asc") {
      return a.full_name.localeCompare(b.full_name);
    } else {
      return b.full_name.localeCompare(a.full_name);
    }
  });

  const handleSelectStudent = (username: string) => {
    setSelectedStudents((prevSelected) =>
      prevSelected.includes(username)
        ? prevSelected.filter((user) => user !== username)
        : [...prevSelected, username]
    );
  };
  const handleSettingsAction = async (action: string) => {
    if (action === "removefromclass") {
      const response = await dispatch(
        removeStudentData({ students: selectedStudents, class_code: classcode })
      );
      if (response.payload.success) {
        dispatch(fetchClassDetails(classcode));
        dispatch(fetchStudents(classcode));
        setSelectedStudents([]);
      }
    }
    if (action === "addtoanotherclass") {
      const response = await dispatch(fetchClasses());
      console.log("response ", response);
      setShowModal(false);
      setShowClassModal(true);
    }
    setShowModal(false);
  };
  const handleConfirmAddToClass = async (newClassCode: string) => {
    setSelectedClass(newClassCode)
    const newObj = {
      class_code: newClassCode,
      students: selectedStudents
    }
    localStorage.setItem('addToAotherClass',JSON.stringify(newObj));
  };
  const handleSubmit = () =>{
    const submissionData = localStorage.getItem('addToAotherClass')
    console.log('Into handlesubmit ',submissionData,typeof submissionData);
    dispatch(addStudent(JSON.parse(submissionData)));
  }
  if (listClassesLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Loading />
      </div>
    );
  }
  return (
    <section>
      <h3 className="text-lg font-semibold mb-3">Student roster</h3>
      <div className="flex justify-between items-center mb-3 bg-accent rounded">
        <button
          className=" px-3 py-2"
          onClick={() =>
            router.push(`/dashboard/class/${classcode}/create-student`)
          }
        >
          + add student
        </button>
        <button className=" px-3 py-2" onClick={() => setShowSearch(true)}>
          <Search size={20} />
        </button>
        <button className=" px-3 py-2" onClick={handleSortingOrder}>
          <ArrowDownUp size={20} />
        </button>
        <button className=" px-3 py-2" onClick={() => setShowModal(true)}>
          <Settings size={20} />
        </button>
      </div>
      {showSearch && (
        <div className="flex items-center my-2">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="px-3 py-2 rounded-l border"
            placeholder="Search students"
          />
          <button className=" px-3 py-2" onClick={() => setShowSearch(false)}>
            <X size={20} />
          </button>
        </div>
      )}
      <div className="space-y-3">
        {sortedData?.map((student) => (
          <div
            className="flex items-center p-3 bg-white rounded-lg border"
            key={student.username}
          >
            <input
              type="checkbox"
              className="mr-3"
              checked={selectedStudents.includes(student.username)}
              onChange={() => handleSelectStudent(student.username)}
            />
            <div>
              <p>{student.full_name}</p>
              <p className="text-gray-500">Username: {student.username}</p>
            </div>
          </div>
        ))}
      </div>
      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white p-2 rounded-lg w-[80%]">
            <div className=" flex justify-end">
              <button
                className="px-3 py-2 mb-2"
                onClick={() => setShowModal(false)}
              >
                <X size={20} />
              </button>
            </div>
            <div className="flex flex-col p-5 gap-4">
              <button
                className={`mb-2 text-black rounded font-lg text-xl ${
                  selectedStudents.length === 0 ? "pointer-events-none" : "auto"
                }`}
                onClick={() => handleSettingsAction("removefromclass")}
              >
                Remove from class
              </button>
              <button
                className={`text-black rounded font-lg text-xl 4 ${
                  selectedStudents.length === 0 ? "pointer-events-none" : "auto"
                }`}
                onClick={() => handleSettingsAction("addtoanotherclass")}
              >
                Add to another class
              </button>
            </div>
          </div>
        </div>
      )}
      {showClassModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white p-5 rounded-lg w-[80%]">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-semibold">Select a class</h3>
              <button
                className="px-3 py-2"
                onClick={() => setShowClassModal(false)}
              >
                <X size={20} />
              </button>
            </div>
            <div className="bg-blue-100 p-3 rounded-lg mb-5 h-60 overflow-y-auto">
              {listClassesData.map((cls) => (
                <div
                  key={cls.classroom_code}
                  className={`p-2 cursor-pointer ${cls.classroom_code === selectedClass ? 'bg-blue-200' : ''}`}
                  onClick={() => handleConfirmAddToClass(cls.classroom_code)}
                >
                  {cls.classroom_title}
                </div>
              ))}
            </div>
            <div className="flex justify-between">
              <button
                className="bg-blue-500 text-white px-4 py-2 rounded"
                onClick={() => setShowClassModal(false)}
              >
                Back
              </button>
              <button
                className="bg-blue-500 text-white px-4 py-2 rounded"
                onClick={handleSubmit}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default ClassViewStudentDetails;
