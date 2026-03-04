# AnyCommerce API - Project Context & Guidelines

## 1. Project Identity
*   **Name:** AnyCommerce API
*   **Type:** E-commerce Backend Service
*   **Goal:** Provide a robust, scalable backend for e-commerce platforms, handling products, users, and secure payments.
*   **Aesthetic:** Clean, structured, and modular (Backend focus).

## 2. Technology Stack
*   **Backend:**
    *   **Language:** Python 3.13+
    *   **Framework:** FastAPI 0.110+
    *   **Database:** MongoDB exclusively (using `PyMongo`).
    *   **Key Libs:** `pydantic`, `stripe`, `python-jose` (JWT), `passlib`, `uvicorn`.
*   **Integrations:**
    *   **Payments:** Stripe (Checkout Sessions, Payment Intents, Webhooks).
    *   **External APIs:** Countries API, Currency Conversion API.

## 3. Architecture & Structure
*   **Entry Point:** `main.py` (FastAPI app initialization and router inclusion).
*   **Source Code (`src/`):**
    *   **Routers (`src/routers/`):** API endpoints grouped by domain (auth, products, user, stripe, catalogs).
    *   **Models (`src/models/`):** Pydantic models for data validation and API responses.
        *   `src/models/request/`: Validates incoming data.
        *   `src/models/responses/`: Standardizes outgoing data.
    *   **Database Abstraction (`src/database/mongodb/`):**
        *   `collection/`: Data access logic (CRUD operations).
        *   `schema/`: PyMongo-specific data structures.
    *   **Environment (`src/env_variables/`):** Modular configuration using `pydantic-settings`.
    *   **Utilities (`src/utils/`):** Shared constants, error IDs, and helper functions.
    *   **Shared (`src/shared/`):** Generic exception handlers and response wrappers (`Data[T]`, `Error[T]`).

## 4. Coding Standards & Conventions
*   **FastAPI Patterns:**
    *   Use **Dependency Injection** (`Depends`) for authentication and database clients.
    *   Standardize responses using the `Data` or `Error` generic models found in `src/shared/generics.py`.
*   **Pydantic:**
    *   Leverage Pydantic v2 features for validation and alias handling.
    *   Use `model_config` with `extra="allow"` sparingly, only when external API data is unpredictable.
*   **Error Handling:**
    *   Use custom `HttpException` from `src/shared/exceptions.py`.
    *   Reference `ErrorsIDs` and `ErrorsDescriptions` from `src/utils/constants.py` for consistent error reporting.
*   **Naming Conventions:**
    *   Python: `snake_case` for functions and variables.
    *   API Fields: `camelCase` for consistency with frontend expectations.

## 5. Security & Restrictions
*   **Authentication:**
    *   **Bearer Token:** Secure endpoints using OAuth2 with JWT.
    *   **API Key:** Internal/Private endpoints require `x-api-key` validation (see `dependencies/auth.py`).
*   **Sensitive Data:**
    *   Passwords must be hashed using `passlib` (bcrypt) before storage.
*   **Payment Security:**
    *   Handle Stripe logic exclusively on the backend.
    *   Use Webhooks for async payment status updates to prevent client-side manipulation.
*   **Data Validation:**
    *   NEVER trust client-provided data; always validate via Pydantic models in routers.

## 6. Development Workflow
1.  **Environment Setup:** Ensure `.env` is populated with all variables defined in `src/env_variables/env.py`.
2.  **Running Locally:**
    ```bash
    python main.py
    ```
    (Runs Uvicorn on the configured host/port with hot-reload enabled).
3.  **API Documentation:** Access Swagger UI at `/docs`.

## 7. Operational Guidelines
*   **Concurrency:** Use `async def` for I/O bound operations (FastAPI default).
*   **Database Persistence:** Ensure session tokens are cleaned up or handled via `cron_tasks.py`.
*   **Environment Management:** NEVER commit secrets to version control.
