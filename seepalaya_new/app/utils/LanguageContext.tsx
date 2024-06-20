'use client';
import { createContext, useState } from "react";
import messagesEN from '@/public/locales/eng.json'
import messagesNP from '@/public/locales/nep.json'
import messageMai from '@/public/locales/mai.json'


type LanguageContextValue = {
    locale: string;
    changeLanguage: (newLocale: string) => void;
    messages: {[key: string]: {[key:string]: string}};
}

const messages = {
    eng: messagesEN,
    nep: messagesNP,
    mai: messageMai,
}

const LanguageContext = createContext<LanguageContextValue>({
    locale: 'eng',
    changeLanguage: (newLocale: string) => {},
    messages: {}
});

const LanguageProvider = ({children}: {children:React.ReactNode}) => {
    const[locale,setLocale] = useState('eng');
    const changeLanguage = (newLocale:string) =>{
        setLocale(newLocale);
    }

    const values =  {locale,changeLanguage,messages};

    return <LanguageContext.Provider value={values}>{children}</LanguageContext.Provider>
}

export {LanguageContext,LanguageProvider};