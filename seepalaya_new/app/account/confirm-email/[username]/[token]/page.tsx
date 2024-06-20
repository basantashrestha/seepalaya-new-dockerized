"use client";
import axios from "axios";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

const VerifyEmail = ({ params }: any) => {
  const { token } = params;
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const new_token = localStorage.getItem("user-auth");
        setLoading(true);
        const response = await axios.post(
          `${process.env.NEXT_PUBLIC_EMAIL_CONFIRMATION_URL}`,
          {
            token,
          },
          {
            headers: {
              Authorization: `Bearer ${new_token}`,
            },
          }
        );
        const success = response.data.success;
        if (success) {
          setLoading(false);
          router.push("/dashboard");
        }
      } catch (error) {
        setLoading(false);
        let backendError = "Encountered an error!. Please try again later.";
        if (axios.isAxiosError(error)) {
          if (error.response?.data?.detail) {
            backendError = error.response?.data?.detail;
          } else {
            backendError = error.response?.data?.message;
          }
        }
        setStatus(backendError);
      }
    };
    fetchData();
  }, []);
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        Loading...
      </div>
    );
  }
  return (
    <>
      {status && (
        <div className="h-screen max-w-md">
          <div className="text-red-500 text-center mt-20">{status}</div>
          <div className="text-center mt-4">
            <button
              className="bg-quarternary hover:bg-quarternary rounded-[25px] text-tertiary text-2xl px-4 py-2"
              onClick={() => router.push("/dashboard")}
            >
              Go to Dashboard
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default VerifyEmail;
