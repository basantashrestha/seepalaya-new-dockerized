import EmailSent from "@/public/email-sent.png";
import Image from "next/image";
const ForgotPasswordDone = () => {
  return (
    <div className="mt-20 w-[90%] mx-auto">
      <div className="flex justify-center">
        <Image src={EmailSent} alt="email sent" />
      </div>
      <div className="mt-5 flex flex-col items-center">
        <p className="text-center">
          Hi there! Please take a moment to verify your email by
          <span className="font-bold"> clicking the link</span> we sent you.
        </p>
        <span>Thanks!</span>
      </div>
    </div>
  );
};

export default ForgotPasswordDone;
