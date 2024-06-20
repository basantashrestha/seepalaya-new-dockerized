"use client";
import { useRouter } from "next/navigation";
import React, { useState } from "react";
import { ArrowLeft } from "lucide-react";

type Role = 'learner' | 'teacher';
const SignUp = () => {
  const router = useRouter();
  const [isRoleSelected,setIsRoleSelected] = useState({learner: false,teacher: false});

  const handleRoleSelection = (val: Role) => {
    setIsRoleSelected({
      learner: false,
      teacher: false,
      [val]: true
    });
    setTimeout(()=>{
      router.push(`choose-role/${val}/signup`);
    },250)
  }
  return (
    <section className="mt-20">
      <button className="px-2 py-2 bg-grayish ml-3 rounded cursor-pointer" onClick={() => router.push('/account/login')}>
        <ArrowLeft />
      </button>
      <div className="flex flex-col w-[90%] mx-auto max-w-7xl mt-8">
        <h3 className="text-3xl font-normal mb-[20px] text-secondary max-w-xl mx-auto">
          Use Seepalaya as a
        </h3>
        <div className="flex flex-col gap-5">
          <button className={`${isRoleSelected.learner ? 'bg-primary': 'bg-grayish'} py-3 rounded flex items-center gap-2 hover:outline`} onClick={() => handleRoleSelection('learner')} >
            <input className="w-7 h-6 ml-5" type="radio" name="role" value="learner" checked={isRoleSelected.learner} onChange={() => handleRoleSelection('learner')}/>
            <span>Learner</span>
          </button>
          <button className={`${isRoleSelected.teacher ? 'bg-primary': 'bg-grayish'} py-3 rounded flex items-center gap-2 hover:outline`} onClick={() => handleRoleSelection('teacher')} >
          <input className="w-7 h-6 ml-5" type="radio" name="role" value="teacher" checked={isRoleSelected.teacher} onChange={() => handleRoleSelection('teacher')}/>
            <span>Teacher/Guardian</span>
          </button>
        </div>
      </div>
    </section>
  );
};

export default SignUp;
