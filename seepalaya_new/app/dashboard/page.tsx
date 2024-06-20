"use client";

import { useRouter } from "next/navigation";
import axios from "axios";
import { useEffect, useState } from "react";
import { Plus } from "lucide-react";

const DashboardPage = () => {
  const router = useRouter();
  const [error, setError] = useState("");
  const [logoutError, setLogoutError] = useState("");
  const [user, setUser] = useState("");
  const [isTeacher, setIsTeacher] = useState(false);

  useEffect(() => {
    setUser(localStorage.getItem("user") || "");
    setIsTeacher(localStorage.getItem("isTeacher") === "true");
  }, []);

  const handleVerifyEmail = async () => {
    setError("");
    const token = localStorage.getItem("user-auth") || "";
    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_RESEND_EMAIL_CONFIRMATION_URL}`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const isSuccess = await response.data.success;
      if (isSuccess) {
        router.push("/account/resend-email-confirmation/done");
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
      setError(backendError);
    }
  };

  const handleLogout = async () => {
    const token = localStorage.getItem("user-auth");
    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_LOGOUT_URL}`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const success = response.data.success;
      if (success) {
        localStorage.removeItem("user-auth");
        localStorage.removeItem("user");
        localStorage.removeItem("isTeacher");
        router.push("/account/login");
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
      setLogoutError(backendError);
    }
  };
  return (
    <>
      <div className="flex justify-between shadow-md h-16 items-center">
        <div className="ml-5">Dashboard page</div>
      </div>
      {user && (
        <div className="flex flex-col justify-evenly gap-5 mt-20 w-[90%] mx-auto max-w-lg">
          {user && (
            <span className="text-center text-lg font-semibold">
              Welcome {user}
            </span>
          )}
          <button
            className="bg-primary text-tertiary px-4 py-2 rounded-lg"
            onClick={() => handleLogout()}
          >
            Log Out
          </button>
          {logoutError && (
            <div className="text-red-500 text-center">{logoutError}</div>
          )}
          <button
            className="bg-primary text-tertiary px-4 py-2 rounded-lg"
            onClick={() => handleVerifyEmail()}
          >
            Verify Email
          </button>
          {error && (
            <div className="text-red-500 text-center mt-4">{error}</div>
          )}
        </div>
      )}
      {isTeacher && (
        <div className="flex justify-between mt-20 w-[90%] max-w-lg mx-auto">
          <span>Create a Class</span>
          <button onClick={() => router.push('/dashboard/class/')}>
            <Plus />
          </button>
        </div>
      )}
    </>
  );
};

export default DashboardPage;
