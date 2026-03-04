# AnyCommerce API - E-Commerce Backend

AnyCommerce API is a high-performance, modular e-commerce backend built with **FastAPI** and **MongoDB**. It provides a secure and scalable foundation for modern commerce applications, featuring deep **Stripe** integration and a structured data architecture.

## Features

-   **Robust Authentication**: JWT-based security with session management and API key validation.
-   **Product & Catalog Management**: Sophisticated handling of complex product metadata and categories.
-   **Secure Payments**: Full Stripe integration (Checkout, Payment Intents, Webhooks).
-   **User Profiles**: Comprehensive user data management including addresses and preferences.
-   **Standardized API**: Consistent response formats and centralized error handling.
-   **Modular Design**: Clear separation between business logic, data models, and database access.

## Prerequisites

-   **Python**: 3.14.2
-   **MongoDB**: A running instance (Local or Cloud).
-   **Pip**: 25.3+

## Installation

1.  **Clone or Download** the repository.
2.  **Navigate** to the project directory:
    ```bash
    cd Anycommerce-Backend
    ```
3.  **Create a Virtual Environment**:
    ```bash
    python -m venv .venv
    ```
4.  **Activate the Environment**:
    -   Windows: `.venv\Scripts\activate`
    -   Mac/Linux: `source .venv/bin/activate`
5.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
6.  **Environment Variables**:
    Create a `.env` file based on the requirements in `src/env_variables/env.py`:
    ```env
    PORT=8000
    HOST=127.0.0.1
    MONGODB_CONNECTION_STRING=your_mongodb_uri
    MONGODB_DATABASE=anycommerce
    AUTH_SECRET_KEY=your_secret_key
    STRIPE_SECRET_KEY=your_stripe_key
    # ... other variables
    ```

## Running the Application

1.  **Start the Server**:
    ```bash
    python main.py
    ```
2.  **Access the API Documentation**:
    Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive Swagger UI.

## Development with PyCharm

1.  **Open Project**:
    -   Open PyCharm and select **Open**.
    -   Navigate to the `Anycommerce-Backend` folder and click **OK**.

2.  **Configure Interpreter**:
    -   Go to **File > Settings > Project: Anycommerce-Backend > Python Interpreter**.
    -   Select your `.venv\Scripts\python.exe`.

3.  **Run Configuration**:
    -   Go to **Run > Edit Configurations**.
    -   Create a new **Python** configuration.
    -   **Script path**: `main.py`
    -   **Working directory**: Path to project root.
    -   Click **OK**.

4.  **Run**: Click the green **Play** button to start the server.
