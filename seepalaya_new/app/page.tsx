import Image from "next/image";
import Logo from "@/public/logo.png";
import Button from "@/components/Button";
import Dropdown from "@/components/Dropdown";

export default function Home() {
  return (
    <section className="bg-primary h-screen">
      <div className=" w-[80%] mx-auto pt-28">
        <div className="flex justify-center ">
          <Image src={Logo} alt="logo" priority/>
        </div>

        <div className="mt-20 flex flex-col  gap-2 max-w-md mx-auto">
          <span className="text-tertiary">Select language</span>
          <Dropdown />
        </div>
        <div className="text-center mt-20">
          <Button label="Get Started" routePath="/account/login" />
        </div>
      </div>
    </section>
  );
}
