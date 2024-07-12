const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");
const axios = require("axios");
const multer = require("multer");

const app = express();
const port = 3001;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Multer setup for file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Route to handle PDF uploads
app.post("/search_pdf", upload.single("pdf_file"), async (req, res) => {
  const fileBuffer = req.file.buffer;

  try {
    const formData = new FormData();
    formData.append("pdf_file", fileBuffer, req.file.originalname);

    const response = await axios.post(
      "http://localhost:8000/search_pdf",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    res.json(response.data);
  } catch (error) {
    console.error(error);
    res
      .status(500)
      .json({ error: "An error occurred while uploading the PDF." });
  }
});

// Route to handle Wikipedia searches
app.post("/search_wiki", async (req, res) => {
  const { wikipedia_title } = req.body;

  try {
    const response = await axios.post("http://localhost:8000/search_wiki", {
      wikipedia_title,
    });

    res.json(response.data);
  } catch (error) {
    console.error(error);
    res
      .status(500)
      .json({ error: "An error occurred while fetching Wikipedia data." });
  }
});

// Route to generate answer (assuming you have this endpoint in your FastAPI backend)
app.post("/generate-answer", async (req, res) => {
  const { user_prompt, question } = req.body;

  try {
    const response = await axios.post("http://localhost:8000/generate-answer", {
      user_prompt,
      question,
    });

    res.json(response.data);
  } catch (error) {
    console.error(error);
    res
      .status(500)
      .json({ error: "An error occurred while generating the answer." });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
