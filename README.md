# FRC-Alberthon

This repository contains the code for **FRC-Alberthon**, a Generative AI project developed for the French Red Cross to assist volunteers during "Accueil–Écoute–Orientation" (AEO) interviews. The application aims to provide relevant information and guidance by transcribing audio questions, analyzing user needs, and suggesting appropriate services.

-----

## Project Structure

```
scarler04-frc-alberthon.git/
├── README.md
├── app.py
├── pyproject.toml
├── static/
│   ├── data-solinum/
│   │   ├── soliguide_response.json
│   │   └── update_data.py
│   ├── image/
│   └── pdf/
└── templates/
    └── index.html
```

  - **`README.md`**: This file.
  - **`app.py`**: The main Flask application that handles web routes, audio processing, natural language understanding, translation, and text-to-speech functionalities.
  - **`pyproject.toml`**: Project configuration file, including dependencies managed by Poetry.
  - **`static/`**: Contains static assets for the web application.
      - **`data-solinum/`**: Stores data, notably `soliguide_response.json`, which is a sample of Soliguide's services and places database. `update_data.py` performs this extract.
      - **`image/`**: Directory for images.
      - **`pdf/`**: Directory for PDF documents.
  - **`templates/`**: Contains HTML templates for the web interface.
      - **`index.html`**: The main HTML file for the application's user interface.

-----

## Features

  - **Audio Transcription**: Utilizes OpenAI's Whisper model to transcribe audio input from users.
  - **Natural Language Understanding**: Leverages OpenAI's GPT-4 to extract key information (age, language, area code) from transcribed audio to identify user needs.
  - **Service Suggestion**: Based on extracted user information, the application queries a local `soliguide_response.json` database to suggest relevant places and services.
  - **Multilingual Support**: Includes a translation feature using Google Cloud Translate and text-to-speech using Google Cloud Text-to-Speech to communicate in various languages.
  - **AI Assistant for Volunteers**: Provides AI-generated responses to volunteer questions, based on Red Cross guidelines and Soliguide data.
  - **Web Interface**: A Flask-based web application for user interaction, including audio recording and playback.

-----

## How to Run the Project

Follow these steps to set up and run the FRC-Alberthon project locally:

### Step 1: Create the Virtual Environment and Install Dependencies

This project uses **Poetry** for dependency management. If you don't have Poetry installed, you can find instructions on their [official website](https://www.google.com/search?q=https://python-poetry.org/docs/%23installation).

Navigate to the root directory of the project in your terminal and run:

```bash
poetry install
```

This command will create a virtual environment and install all the necessary Python packages listed in `pyproject.toml`.

### Step 2: Configure Environment Variables

The application requires an OpenAI API key and Google Cloud credentials.

1.  **OpenAI API Key**: Create a `.env` file in the root directory of the project and add your OpenAI API key:

    ```
    OPENAI_API_KEY="your_openai_api_key_here"
    ```

2.  **Google Cloud Credentials**: Ensure your Google Cloud service account key file is accessible. The `app.py` currently has a hardcoded path. For local testing, you might need to adjust this line in `app.py`:

    ```python
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Your\Path\Here\*.json"
    ```

    Replace `r"C:\Your\Path\Here\*.json"` with the actual path to your Google Cloud service account JSON key file.

### Step 3: Run the Application

Once the dependencies are installed and environment variables are set, run the Flask application using Poetry:

```bash
poetry run python .\app.py
```

The application will start, and you can access it by navigating to `http://127.0.0.1:5000/` in your web browser.

-----

## Usage

The application provides a web interface where users can interact with the AI assistant. Key functionalities include:

  - **Asking Questions**: Users can either type their general questions or record audio for specific aid suggestions (The main goal is to record the whole conversation and use other functionalities during that time).
  - **Receiving Answers**: The AI processes the input and provides formatted responses, including relevant information and service suggestions.
  - **Translation**: A translation feature allows converting text between different languages.
  - **Text-to-Speech**: AI-generated responses can be converted into speech for accessibility.

-----

## Contact

For any inquiries or feedback, please contact the authors:

  - Rémi Moreau: rmoreau@albertschool.com
  - Yann MEUROU: ymeurou2702@gmail.com
