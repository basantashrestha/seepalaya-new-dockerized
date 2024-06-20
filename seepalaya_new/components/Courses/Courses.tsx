"use client";
import React, { useContext } from "react";
import Image1 from "@/public/image1.png";
import Image from "next/image";
import { LanguageContext } from "@/app/utils/LanguageContext";
import { useRouter } from "next/navigation";

const Courses = () => {
  const { locale, messages } = useContext(LanguageContext);
  const router = useRouter();
  return (
    <section className="relative top-20 w-[100%] py-[20px] bg-section h-calc-100percent-5rem">
      <div className="flex flex-col w-[80%] mx-auto max-w-6xl">
        <h2 className="text-3xl font-semibold mb-[20px] text-secondary">
          {messages[locale].explore}
        </h2>
        <div className="flex flex-col gap-2 lg:flex-row">
          <div className="flex flex-col bg-primary basis-2/4 p-16 items-center">
            <h3 className="font-bold text-secondary text-2xl mb-10">
              {messages[locale].track}
            </h3>
            <p className="text-secondary mb-1">{messages[locale].signinInfo}</p>
            <p className="text-secondary text-center">
              {messages[locale].addCourseInfo}
            </p>
            <div className="mt-10 flex gap-5">
              <button className="px-4 py-2 uppercase bg-tertiary text-white rounded" onClick ={() =>router.push('/account/login')}>
                {messages[locale].login}

              </button>
              <button className="border border-tertiary px-4 py-2 uppercase text-tertiary rounded" onClick ={() =>router.push('/account/signup')} >
                {messages[locale].signup}
              </button>
            </div>
          </div>
          <div className="basis-2/4 bg-quarternary">
            <Image src={Image1} alt="Account login" />
          </div>
        </div>
      </div>
    </section>
  );
};

export default Courses;
