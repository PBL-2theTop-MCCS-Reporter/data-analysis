# MCCS Analysis AI Generation Report LLM

This project contains a Streamlit-based dashboard for email marketing analysis and a backend AI generation component utilizing a Retrieval-Augmented Generation (RAG) model.

---

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You need to have [Conda](https://docs.conda.io/en/latest/miniconda.html) installed to manage the project's environment and dependencies.

### Installation & Setup

Follow these steps to set up the project environment:

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Create a new Conda environment:**
    This command creates a new virtual environment named `venv` with a specified Python version.
    ```bash
    conda create -n venv python
    ```

3.  **Activate the Conda environment:**
    You must activate the environment each time you work on the project.
    ```bash
    conda activate venv
    ```

4.  **Install required packages:**
    This command installs all the necessary libraries and dependencies listed in the `new_requirements.txt` file.
    ```bash
    pip install -r new_requirements.txt
    ```

---

## 🖥️ Usage

Once the setup is complete, you can run the different components of the application.

### Running the Streamlit Dashboard

To launch the email marketing dashboard, run the following command in your terminal:

```bash
if dimension issue happend, use command: "python -m src.RAG.main" at root path to update the rag vector
streamlit run email_marketing_dashboard/app.py
```

### Running the Full-Functioning Dashboard

To launch the full-functioning dashboard that will actually be running as-is for MCCS:
1. Download all necessary libraries through the requirements.txt
2. Create a .env file in the root directory
3. Create a new environment variable called OPENAI_API_KEY
4. Paste in the API key
5. Run the dashboard from the root directory using "streamlit run src/dashboard.py"
