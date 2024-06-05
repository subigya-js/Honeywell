import React from 'react';
import { SiChatbot } from "react-icons/si";

const Navbar = () => {
    return (
        <div className='h-[10vh] w-screen bg-gray-800 flex items-center text-gray-200 px-5 font-navFont shadow-4xl'>
            <div className='flex justify-between text-xl items-center'>ResQ <span className='pl-2'><SiChatbot /></span></div>
        </div>
    );
}

export default Navbar;
