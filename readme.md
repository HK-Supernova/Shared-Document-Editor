# Shared Document Editor

A POC for secured web app for live collaboration on text documents.

## Quick Start
1. Build and run with Docker Compose:
   ```bash
   cd app
   docker-compose build
   docker-compose up
    ```
2. Open your browser at:<br>
   `http://localhost` (will redirect automatically to https)

3. Log in with one of the predefined users:<br>
    username, password<br>
    `test1, test1715`<br>
    `test2, test1935`

## Highlights
* **Secured**: Traffic goes through HTTPS.
* **Instant collaboration**: Edits appear in real time for other connected users - no "Save" button required.
* **Multi-session**: A single user can connect from multiple devices and still see live updates.
* **Logging**: Every login and keystroke is recorded in the database, including timestamps and cursor positions.
