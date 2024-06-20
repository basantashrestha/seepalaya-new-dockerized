'use client';
import Image from "next/image";
import DarkModeBulb from '@/public/darkmode_bulb.png';
import LightModeBulb from '@/public/lightmode_bulb.png';
import Logo from '@/public/logo.png';
import { useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { LanguageContext } from "@/app/utils/LanguageContext";


const Navbar = () => {
  const router = useRouter();
  const {locale,changeLanguage,messages} = useContext(LanguageContext);
  const [theme,setTheme] = useState('light');
  useEffect(()=>{
    const selectedTheme = localStorage.getItem('theme') || 'light';
    setTheme(selectedTheme);
    document.body.classList.add(selectedTheme);
  },[])

  const handleToggle = () =>{
    let newTheme;
    switch(theme){
      case 'dark':
        newTheme = 'light';
        break;
      case 'light':
        newTheme = 'dark';
        break;
      default: 
        newTheme = 'light';
        break;
    }
    setTheme(newTheme);
    localStorage.setItem('theme',newTheme);
    document.body.className = newTheme;
  }
  return (
    <header className="h-20  bg-primary fixed w-[100%] shadow-[0_7px_7px_0px_rgba(0,0,0,0.1)]">
      <nav className="flex justify-between items-center w-[90%] h-[100%] m-auto  ">
        <div className="nav__brand w-[150px] cursor-pointer" onClick={() => router.push('/')}>
          <Image
            src={Logo} 
            alt="Image description"
            className="w-[100%] object-contain "
          />
        </div>
        <div className="nav__items flex h-[100%] items-center gap-5">
            <button className="bg-info hover:bg-infohover text-white px-5 py-2 rounded" onClick={() =>router.push('/account/login')}>{messages[locale].login}</button>
            <button className="bg-info hover:bg-infohover text-white px-5 py-2 rounded" onClick={() =>router.push('/account/signup')}>{messages[locale].signup}</button>
            <select value={locale} onChange={(e) => changeLanguage(e.target.value)}>
              <option value="eng">En</option>
              <option value="nep">ने</option>
              <option value="mai">मै</option>
            </select>
            <button className='text-secondary' onClick={handleToggle}>
              <Image src={theme==='dark' ? DarkModeBulb : LightModeBulb} alt="dark or light mode" />
            </button>
        </div>
      </nav>
    </header>
  );
};

export default Navbar;
