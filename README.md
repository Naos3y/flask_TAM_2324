# MedTrack API

## Description
MedTrack API is a Flask-based REST API designed to support an Android application, helping users manage their medications. It integrates PostgreSQL as the database, JWT for authentication, and a variety of endpoints to manage users and medications, including login, registration, and medication administration tracking.

## Features
- **User Authentication:** Secure login and registration using JWT.
- **Medication Management:** Users can add, edit, and delete their medications.
- **Token-Based Authorization:** Routes are protected by token verification, ensuring secure access to user data.
- **Dose Scheduling and Tracking:** Tracks and records medication dosages and administration history.
- **User Profile Management:** Allows users to view and update their profile.

## Endpoints
- `/login`: Logs in a user and returns an access token.
- `/register`: Registers a new user.
- `/medicamentos`: Retrieves a list of all medications.
- `/get_user_medicamentos`: Retrieves a list of medications for the authenticated user.
- `/insert_medicamento`: Inserts a new medication for the authenticated user.
- `/editar_medicamento`: Edits an existing medication.
- `/apagar_medicamento`: Deletes a medication.
- `/administrar_medicamento`: Records when a medication is administered.
- `/obter_historico`: Retrieves the medication administration history for the authenticated user.

## Technologies Used
- **Backend:** Flask
- **Database:** PostgreSQL
- **Authentication:** JWT
- **Mobile Application:** Android (client)
