import React, { useState } from 'react';
import { IoIosSend } from "react-icons/io";
import fire from '../assets/fire.gif'

const Body = () => {
    const [response, setResponse] = useState("");
    const [prompt, setPrompt] = useState("");
    const [loading, setLoading] = useState(false);

    const handleChange = (event) => {
        setPrompt(event.target.value);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();

        if (!prompt.trim()) {
            return;
        }

        setLoading(true);

        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: prompt }),
            });

            if (!response.ok) {
                throw new Error('Failed to fetch response');
            }

            const responseData = await response.json();
            setResponse(responseData.response.output_text); // Extract 'output_text' from the response
        } catch (error) {
            console.error('Error:', error);
            setResponse('An error occurred while fetching response.');
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (event) => {
        if(event.key === "Enter" && !event.shiftKey) {
            event.preventDefault()
            handleSubmit(event)
        }
    }

    return (
        <div className="h-[90vh] w-[screen] bg-gray-700 flex flex-col justify-between items-center py-5 relative">
            {/* Body */}
            <div className="h-[85%] border border-gray-600 w-[90%] rounded-lg px-5 py-3 text-gray-200 top-0 overflow-y-auto overflow-x-hidden text-justify relative">
                {loading ? (
                    <img src={fire} alt='Loader..' className='h-10 absolute top-[50%] left-[50%] transform-translate-x-1/2 -translate-y-1/2' />
                ) : (
                    <p>{response || "Enter the prompt below..."}</p>
                )}
            </div>

            {/* Input Section */}
            <div className="w-full flex justify-center items-center">
                <form className="flex justify-center items-center pt-4 rounded-lg w-[90%]" onSubmit={handleSubmit}>
                    <textarea
                        type="text"
                        placeholder="Enter the prompt..."
                        className="min-h-[100px] max-h-[200px] w-[80%] p-3 rounded-lg outline-none bg-gray-700 border text-gray-200 flex items-center overflow-auto scrollbar-thin scrollbar-thumb-indigo-300 scrollbar-track-gray-700"
                        onChange={handleChange}
                        onKeyDown={handleKeyDown}
                        value={prompt}
                    />
                    <button type="submit" className="text-white text-2xl hover:scale-125 hover:rotate-12 duration-200 ml-5">
                        <IoIosSend />
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Body;
