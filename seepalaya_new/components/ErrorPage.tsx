import Image from "next/image";
import ErrorImage from "@/public/verify-email.png";

const ErrorPage: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center bg-gray-100 p-4 h-screen">
      <h1 className="text-4xl font-bold mb-4">Oops! Something went wrong.</h1>
      <Image className="w-80 mb-4" src={ErrorImage} alt="Oops!" />
      <p className="text-lg text-gray-700">
        We're sorry, but the page you are looking for cannot be found.
      </p>
    </div>
  );
};

export default ErrorPage;
