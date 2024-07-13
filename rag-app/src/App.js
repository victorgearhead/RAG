// import logo from "./logo.svg";
import "./App.css";
import React, { useState } from "react";
import axios from "axios";

function App() {
  const [userPrompt, setUserPrompt] = useState("");
  const [userToken, setUserToken] = useState("");
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [wikiTitle, setWikiTitle] = useState("");
  // const [pdfFilePath, setPdfFilePath] = useState("");

  const handleGenerateAnswer = async () => {
    try {
      const res = await axios.post("http://localhost:3001/generate-answer", {
        token: userToken,
        user_prompt: userPrompt,
        question: question,
      });
      setResponse(res.data.response);
    } catch (error) {
      console.error(error);
      setResponse("An error occurred while generating the answer.");
    }
  };

  const handleEnterPrompt = () => {
    setUserPrompt(userPrompt);
  };

  const handleEnterToken = () => {
    setUserPrompt(userToken);
  };

  const handleWiki = async () => {
    try {
      const res = await axios.post("http://localhost:8000/search_wiki", {
        wikipedia_title: wikiTitle,
      });
      console.log(res.data);
      setResponse("Wikipedia data fetched and stored.");
    } catch (error) {
      console.error(error);
      setResponse("An error occurred while fetching Wikipedia data.");
    }
  };

  const handlePDF = async (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("pdf_file", file);
    try {
      const res = await axios.post(
        "http://localhost:8000/search_pdf",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      console.log(res.data);
      setResponse("PDF data fetched and stored.");
    } catch (error) {
      console.error(error);
      setResponse("An error occurred while fetching PDF data.");
    }
  };

  return (
    <>
      <div className="container-fluid vh-100 d-flex bg-secondary justify-content-center align-items-center">
        <div className="row w-100 h-100">
          <div className="col-md-2 d-flex flex-column">
            <div className="card bg-black text-white h-100">
              <div className="card-body d-flex flex-column justify-content-between">
                <div className="mb-4">
                  <p>Enter the prompt for Llama3 to respond as:</p>
                  <label htmlFor="userPrompt">Give Prompt here:</label>
                  <div className="input-group">
                    <input
                      type="text"
                      id="userPrompt"
                      value={userPrompt}
                      onChange={(e) => setUserPrompt(e.target.value)}
                      className="form-control"
                    />
                    <button
                      className="btn btn-light"
                      onClick={handleEnterPrompt}
                    >
                      Enter
                    </button>
                  </div>
                </div>
                <div className="mb-4">
                  <p>Enter your Hugging Face Token For Llama3:</p>
                  <p>
                    (Get your Token Here https://huggingface.co/settings/tokens
                    and permission for Llama3 here
                    https://huggingface.co/meta-llama/Meta-Llama-3-8B)
                  </p>
                  <label htmlFor="userToken">Enter Token Here:</label>
                  <div className="input-group">
                    <input
                      type="text"
                      id="userToken"
                      value={userToken}
                      onChange={(e) => setUserToken(e.target.value)}
                      className="form-control"
                    />
                    <button
                      className="btn btn-light"
                      onClick={handleEnterToken}
                    >
                      Enter
                    </button>
                  </div>
                </div>
                <div className="text-center" style={{ paddingTop: "150px" }}>
                  <p>
                    All the conversation with LLM and all the data used for RAG
                    are stored in database different from Emails'. User can
                    delete this with a caution of clearance of whole data.
                  </p>
                  <p>View and Delete History</p>
                  <button
                    className="btn btn-light w-100 mb-2"
                    // onClick={pythonConvHistory}
                  >
                    View History
                  </button>
                  <button
                    className="btn btn-light w-100"
                    // onClick={pythonConvDelete}
                  >
                    Delete History
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-8 d-flex flex-column">
            <div className="card bg-black text-white h-100">
              <div className="card-body d-flex flex-column justify-content-between">
                <div className="mb-4">
                  <label htmlFor="response">Chatbot's Reply</label>
                  <textarea
                    id="response"
                    value={response}
                    className="form-control mb-4"
                    rows="25"
                    readOnly
                  ></textarea>
                </div>
                <div className="mb-4">
                  <label htmlFor="question">Input Question</label>
                  <div className="input-group">
                    <input
                      type="text"
                      id="question"
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      className="form-control"
                    />
                    <button
                      className="btn btn-light"
                      onClick={handleGenerateAnswer}
                    >
                      Send
                    </button>
                  </div>
                </div>
                <div>
                  <label htmlFor="wikipidea">About</label>
                  <div className="input-group">
                    <input
                      type="text"
                      id="wikipideaTitle"
                      value={wikiTitle}
                      onChange={(e) => setWikiTitle(e.target.value)}
                      className="form-control"
                    />
                    <button className="btn btn-light" onClick={handleWiki}>
                      Search Wiki
                    </button>
                  </div>
                </div>
                <div>
                  <label htmlFor="pdfFile">Upload PDF</label>
                  <div className="input-group">
                    <input
                      type="file"
                      id="pdfFile"
                      onChange={handlePDF}
                      className="form-control"
                    />
                    <button className="btn btn-light" onClick={handlePDF}>
                      Upload PDF
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
