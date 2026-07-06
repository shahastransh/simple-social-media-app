# Simple Social Media App

A lightweight, Python-based social media application. This project features a modular backend for handling users, images, and database operations, alongside a dedicated frontend script. 

## Project Structure

Based on the repository layout, the project is organized as follows:

*   **`app/`**: Contains the core backend modules.
    *   `app.py`: Core application logic and routing.
    *   `db.py`: Database connection and query execution.
    *   `images.py`: Image processing and handling logic.
    *   `schema.py`: Data models and validation schemas.
    *   `user.py`: User management and authentication flows.
*   **`Frontend.py`**: The frontend user interface for the application.
*   **`main.py`**: The primary entry point for the backend server.
*   **`pyproject.toml` & `uv.lock`**: Project metadata and dependency lock files, managed by the `uv` package manager.
*   **`test.db`**: A local SQLite database file for rapid development and testing.
*   **`.python-version`**: Specifies the exact Python version required for this project.

## Prerequisites

Before running the application, ensure you have the following installed on your system:
*   **Python**: Check the `.python-version` file for the exact required version.
*   **uv**: An extremely fast Python package installer and resolver. You can install it via curl, pip, or brew (see the [uv documentation](https://github.com/astral-sh/uv) for details).

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd simple-social-media-app
    ```

2.  **Install dependencies:**
    This project uses `uv` for dependency management. Install the required packages by running:
    ```bash
    uv sync
    ```
    *(This will read from `pyproject.toml` and `uv.lock` to set up your environment.)*

3.  **Run the application:**
    You will likely need to start the backend and frontend separately or via the main entry point:
    
    To run the backend server:
    ```bash
    python main.py
    ```
    
    To run the frontend interface:
    ```bash
    python Frontend.py
    ```
    *(Note: If `Frontend.py` is built with a framework like Streamlit, use `streamlit run Frontend.py` instead).*

## Database

The application currently defaults to a local SQLite database (`test.db`) for easy setup and testing. All database interactions and schemas are defined within `app/db.py` and `app/schema.py`.