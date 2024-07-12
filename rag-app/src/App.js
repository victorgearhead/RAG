// import logo from "./logo.svg";
import "./App.css";
import React, { useState } from "react";

const pythonPrompt = () => {};
const pythonConvHistory = () => {};
const pythonConvDelete = () => {};
const pythonReply = () => {};
const pythonWiki = () => {};
const pythonUploadPDF = () => {};
const pythonSend = () => {};
const pythonInbox = () => {};
const pythonEmailData = () => {};
const pythonEmailDelete = () => {};

function App() {
  return (
    <>
      <div className="container-fluid vh-100 d-flex bg-secondary justify-content-center align-items-center">
        <div className="row w-100 h-100">
          {/* Left Card */}
          <div className="col-md-2 d-flex flex-column">
            <div className="card bg-black text-white h-100">
              <div className="card-body d-flex flex-column justify-content-between">
                <div className="mb-4">
                  <p>Enter the prompt for Llama3 to respond as:</p>
                  <label htmlFor="character">Give Prompt here:</label>
                  <div className="input-group">
                    <input
                      type="text"
                      id="character"
                      name="character"
                      className="form-control"
                    />
                    <button className="btn btn-light" onClick={pythonPrompt}>
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
                    onClick={pythonConvHistory}
                  >
                    View History
                  </button>
                  <button
                    className="btn btn-light w-100"
                    onClick={pythonConvDelete}
                  >
                    Delete History
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Center Card */}
          <div className="col-md-8 d-flex flex-column">
            <div className="card bg-black text-white h-100">
              <div className="card-body d-flex flex-column justify-content-between">
                <div className="mb-4">
                  <label htmlFor="chatbot-reply">Chatbot's Reply</label>
                  <textarea
                    id="chatbot-reply"
                    name="chatbot-reply"
                    className="form-control mb-4"
                    rows="25"
                    readOnly
                  ></textarea>
                </div>
                <div className="mb-4">
                  <label htmlFor="input-sentence">Input Sentence</label>
                  <div className="input-group">
                    <input
                      type="text"
                      id="input-sentence"
                      name="input-sentence"
                      className="form-control"
                    />
                    <button className="btn btn-light" onClick={pythonReply}>
                      Send
                    </button>
                  </div>
                </div>
                <button
                  className="btn btn-secondary w-100 mb-4"
                  onClick={pythonWiki}
                >
                  Search Wikipidea
                </button>
                <button
                  className="btn btn-secondary w-100"
                  onClick={pythonUploadPDF}
                >
                  Upload PDF
                </button>
              </div>
            </div>
          </div>

          {/* Right Card */}
          <div className="col-md-2 d-flex flex-column">
            <div className="card bg-black text-white h-100">
              <div className="card-body d-flex flex-column justify-content-between">
                <div className="mb-4">
                  <label htmlFor="email">Email</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    className="form-control"
                  />
                  <label htmlFor="password" className="mt-2">
                    Password
                  </label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    className="form-control"
                  />
                  <label>To</label>
                  <input type="text" className="form-control mb-2" />
                  <label>Body</label>
                  <input type="text" className="form-control" />
                </div>
                <div className="d-flex justify-content-between mb-2">
                  <button className="btn btn-light w-48" onClick={pythonSend}>
                    Send Email
                  </button>
                  <button className="btn btn-light w-48" onClick={pythonInbox}>
                    View Inbox
                  </button>
                </div>
                <div className="text-center" style={{ paddingTop: "150px" }}>
                  <p>
                    Email are used to build RAG Databases to enchance the LLM to
                    tune itself for better interaction with user. User can
                    always delete these databases manually or here itself.
                  </p>
                  <p>View and Delete Datbases</p>
                  <button
                    className="btn btn-light w-100 mb-2"
                    onClick={pythonEmailData}
                  >
                    View Email Data
                  </button>
                  <button
                    className="btn btn-light w-100"
                    onClick={pythonEmailDelete}
                  >
                    Delete Email Data
                  </button>
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
