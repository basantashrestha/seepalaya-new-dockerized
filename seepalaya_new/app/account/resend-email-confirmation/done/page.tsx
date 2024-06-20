import VerifyEmail from "@/public/verify-email.png";
import Image from "next/image";
const ResendEmailDone = () => {
  return (
    <div className="mt-20 w-[90%] mx-auto">
      <div className="flex justify-center">
        <Image src={VerifyEmail} alt="verify email" />
      </div>
      <div className="mt-5 flex flex-col items-center">
        <h3 className="text-center text-3xl font-bold">
          All set!
        </h3>
        <p className="text-center px-3 mt-2 text-xl">Please verify through the email we sent.</p>
      </div>
    </div>
  );
};

export default ResendEmailDone;
