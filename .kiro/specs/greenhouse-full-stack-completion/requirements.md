# Requirements Document

## Introduction

SmartFarmXBot is an IoT greenhouse control system built with React + Vite frontend and Flask backend, deployed on Raspberry Pi 4. The project has a working skeleton with sensor reading, device control, and a dashboard UI, but lacks critical production features: real-time communication, data persistence, authentication, settings storage, camera integration, and automated testing. This document specifies the requirements to complete the system into a fully functional production-ready greenhouse controller.

## Glossary

- **Backend**: The Flask application running on Raspberry Pi that reads sensors, controls GPIO relays, and serves the REST/WebSocket API
- **Frontend**: The React + Vite single-page application that displays sensor data and provides device control UI
- **Sensor_Service**: The backend module responsible for reading DHT22, MCP3008 ADC, and photoresistor values
- **Device_Controller**: The backend module responsible for GPIO relay control with manual override protection and thread-safe locking
- **WebSocket_Server**: The flask-socketio server that broadcasts real-time sensor data and device state changes to connected clients
- **Database**: SQLite database used for persisting sensor history, settings, and user credentials
- **Auth_Service**: The backend module responsible for JWT-based user authentication and token validation
- **Settings_Service**: The backend module responsible for reading and writing automation thresholds and system configuration
- **Camera_Service**: The backend module responsible for Pi Camera MJPEG streaming or graceful fallback when no camera is connected
- **Automation_Engine**: The single backend module that evaluates sensor data against thresholds and issues device commands (replacing duplicate frontend logic)
- **Threshold**: A configurable numeric boundary (temperature, soil moisture, light level) that triggers automated device actions

## Requirements

### Requirement 1: Real-Time WebSocket Communication

**User Story:** As a greenhouse operator, I want to see sensor data and device state updates in real-time without refreshing the page, so that I can monitor conditions and respond to changes immediately.

#### Acceptance Criteria

1. WHEN the Backend starts, THE WebSocket_Server SHALL initialize on the same Flask application using flask-socketio with eventlet or gevent async mode
2. WHEN a client connects to the WebSocket_Server, THE WebSocket_Server SHALL authenticate the connection using the JWT token provided in the handshake auth payload and accept the connection only if the token is valid
3. IF the JWT token is missing or invalid during WebSocket handshake, THEN THE WebSocket_Server SHALL reject the connection and emit a connection error indicating an authentication failure
4. WHILE the Backend is running, THE WebSocket_Server SHALL broadcast a "sensor_update" event containing current sensor readings (temperature, humidity, soilMoisture, light) to all authenticated clients at a configurable interval between 2 and 30 seconds with a default of 5 seconds
5. WHEN the Device_Controller changes a device state, THE WebSocket_Server SHALL emit a "device_update" event containing the updated device snapshot (device states for drip, rain, cooler, led and GPIO status) to all authenticated clients within 1 second
6. IF the WebSocket connection is lost, THEN THE Frontend SHALL attempt reconnection with exponential backoff starting at 1 second, doubling each attempt, up to a maximum interval of 30 seconds, and SHALL continue retrying indefinitely until the connection is restored
7. WHEN a client connects successfully, THE WebSocket_Server SHALL emit an "initial_state" event containing the current sensor readings and the current device states within 2 seconds of connection

### Requirement 2: Sensor History Database Persistence

**User Story:** As a greenhouse operator, I want sensor readings to be stored persistently, so that I can view historical data after system restarts and analyze trends over time.

#### Acceptance Criteria

1. WHEN the Backend starts, THE Database SHALL initialize an SQLite database file in the backend/data directory with a sensor_history table containing columns for id (integer primary key), timestamp (ISO 8601 text), temperature (real), humidity (real), soil_moisture (real), and light (real)
2. WHILE the Backend is running, THE Sensor_Service SHALL insert a new sensor reading row into the sensor_history table at the configured broadcast interval (between 2 and 30 seconds)
3. WHEN the Frontend requests history data via GET /api/history, THE Backend SHALL return sensor readings from the Database as a JSON array sorted by timestamp ascending, filtered by optional "start" and "end" query parameters in ISO 8601 format (default: last 24 hours), limited to a maximum of 1000 readings per response
4. IF the "start" or "end" query parameter is not a valid ISO 8601 string, THEN THE Backend SHALL return an error response with a message indicating the invalid time range format
5. WHILE the Database contains more than 30 days of sensor readings, THE Backend SHALL delete readings older than 30 days during a cleanup cycle that runs once every 24 hours after Backend startup
6. IF the Database write fails, THEN THE Backend SHALL log the error and continue operating without crashing, retrying the database connection on the next scheduled insert

### Requirement 3: JWT Authentication

**User Story:** As a system administrator, I want proper authentication protecting the API and WebSocket, so that only authorized operators can view data and control devices.

#### Acceptance Criteria

1. WHEN the Backend starts, THE Database SHALL contain a users table with columns for id, email, password_hash, name, and role
2. WHEN a user submits valid credentials (matching email and correct password) to POST /api/auth/login, THE Auth_Service SHALL return a JWT access token with a configurable expiration time (default: 24 hours, minimum: 1 hour, maximum: 168 hours) and the user profile containing id, email, name, and role
3. IF a user submits credentials to POST /api/auth/login with an email that does not exist or a password that does not match, THEN THE Auth_Service SHALL return HTTP 401 with an error message indicating invalid credentials without revealing which field was incorrect
4. WHEN a request arrives at any API endpoint other than /api/health and /api/auth/login without a valid JWT token in the Authorization header, THE Backend SHALL return HTTP 401 with an error message indicating missing or invalid authentication
5. WHEN a request arrives with an expired JWT token, THE Backend SHALL return HTTP 401 with a message indicating token expiration
6. WHEN the Frontend receives a 401 response, THE Frontend SHALL remove the greenhouse_user and greenhouse_token entries from localStorage and redirect the user to the login page
7. THE Auth_Service SHALL hash passwords using werkzeug.security generate_password_hash with pbkdf2:sha256 method
8. WHEN the Backend starts with an empty users table, THE Auth_Service SHALL create a default admin user with credentials from environment variables (ADMIN_EMAIL, ADMIN_PASSWORD)
9. IF the Backend starts with an empty users table and ADMIN_EMAIL or ADMIN_PASSWORD environment variables are not set, THEN THE Backend SHALL log an error message indicating the missing variables and exit with a non-zero status code
10. WHEN a WebSocket connection is initiated, THE Backend SHALL require a valid JWT token passed as a query parameter or in the auth handshake, and SHALL reject the connection if the token is missing, invalid, or expired

### Requirement 4: Settings Persistence

**User Story:** As a greenhouse operator, I want my threshold settings and system configuration to persist across page refreshes and server restarts, so that I do not need to reconfigure the system each time.

#### Acceptance Criteria

1. WHEN the Frontend loads the Settings page, THE Frontend SHALL request current settings from GET /api/settings and populate the temperature, moisture, and light threshold sliders with the stored values
2. WHEN the operator releases a threshold slider after changing its value, THE Frontend SHALL send the complete settings object (temperature, moisture, and light thresholds) to POST /api/settings within 1 second
3. WHEN POST /api/settings receives a JSON body containing temperature, moisture, and light threshold values that pass validation, THE Settings_Service SHALL write the settings to the Database and return the saved values as JSON
4. WHEN the Backend starts and saved settings exist in the Database, THE Settings_Service SHALL load those settings and apply them to the Automation_Engine thresholds
5. IF the Backend starts and no saved settings exist in the Database, THEN THE Settings_Service SHALL apply default thresholds of temperature 30°C, moisture 40%, and light 420 lux to the Automation_Engine
6. WHEN POST /api/settings receives threshold values, THE Settings_Service SHALL validate that temperature is between 15 and 50 degrees inclusive, moisture is between 10 and 90 percent inclusive, and light is between 100 and 1000 lux inclusive
7. IF invalid settings values are submitted to POST /api/settings, THEN THE Backend SHALL return HTTP 400 with a JSON response containing a field-level validation error indicating which threshold is out of range and the allowed range
8. IF the Frontend receives an error response from POST /api/settings, THEN THE Frontend SHALL display the validation error to the operator and retain the previous valid slider values
9. IF the Frontend fails to load settings from GET /api/settings due to a network or server error, THEN THE Frontend SHALL display the locally held default threshold values and show an indicator that settings could not be loaded from the server

### Requirement 5: Camera Integration

**User Story:** As a greenhouse operator, I want to view a live camera feed from inside the greenhouse, so that I can visually inspect plant health remotely.

#### Acceptance Criteria

1. WHEN a Pi Camera module is connected and enabled, THE Camera_Service SHALL serve an MJPEG stream at GET /api/camera/stream with Content-Type "multipart/x-mixed-replace" boundary, at a resolution configurable via environment variables (default: 640x480, allowed: 320x240, 640x480, 1280x720, 1920x1080) and frame rate configurable via environment variables (default: 10 fps, allowed range: 1–30 fps)
2. WHEN no Pi Camera module is detected, THE Camera_Service SHALL return HTTP 200 with a JSON response at GET /api/camera/stream containing a field "status" set to "unavailable" and a "message" field indicating the camera hardware was not found
3. WHEN the Frontend requests GET /api/camera, THE Camera_Service SHALL return a JSON response containing the fields: availability (boolean), resolution (string in "WxH" format), frameRate (integer in fps), and streamUrl (string path to the stream endpoint)
4. IF the camera stream encounters a hardware error or library exception during operation, THEN THE Camera_Service SHALL log the error, terminate the active stream response, and return HTTP 503 with a JSON body containing a "message" field indicating temporary unavailability for subsequent requests until the camera recovers
5. IF the Pi Camera module is disconnected while a stream is active, THEN THE Camera_Service SHALL close the stream connection within 5 seconds and set the camera availability status to unavailable until the next successful detection

### Requirement 6: Unified Automation Engine

**User Story:** As a system developer, I want automation logic to run exclusively on the backend, so that there is a single source of truth for device control decisions and no conflicting commands from frontend and backend.

#### Acceptance Criteria

1. THE Automation_Engine SHALL run exclusively on the Backend, evaluating sensor readings against thresholds at a fixed interval of no more than 5 seconds and issuing device commands through the Device_Controller
2. WHEN the Automation_Engine determines a device state change is needed, THE Automation_Engine SHALL call the Device_Controller set_device method with source "auto"
3. THE Frontend SHALL contain no local automation logic that issues device commands (no deriveAutomationState calls that trigger set_device) and SHALL reflect device states solely from Backend updates received via WebSocket or API polling at an interval no greater than 10 seconds
4. WHEN the operator toggles auto mode on the Frontend, THE Frontend SHALL send the auto mode state to the Backend via POST /api/settings/auto-mode
5. WHEN the Backend receives a POST /api/settings/auto-mode request, THE Automation_Engine SHALL enable or disable automation evaluation within 1 second of receiving the request
6. IF the POST /api/settings/auto-mode request fails or returns a non-success response, THEN THE Frontend SHALL retain the previous auto mode display state and present an error message indicating the auto mode change was not applied
7. WHILE auto mode is disabled, THE Automation_Engine SHALL not issue any device commands regardless of sensor readings
8. WHEN thresholds are updated via the Settings_Service, THE Automation_Engine SHALL apply the new thresholds on the next evaluation cycle (within 5 seconds) without requiring a restart
9. IF the Automation_Engine issues a command that is blocked by the Device_Controller manual override (MANUAL_OVERRIDE_SECONDS window), THEN THE Automation_Engine SHALL log the blocked command and skip that device until the next evaluation cycle

### Requirement 7: Storage Module Integration

**User Story:** As a system developer, I want the existing storage.py module to be properly integrated with API endpoints, so that settings read/write functionality is accessible from the frontend.

#### Acceptance Criteria

1. WHEN GET /api/settings is called, THE Backend SHALL use the Settings_Service to read settings from the Database and return a JSON response containing the fields: thresholds (object with temperature, moisture, and light numeric values), autoMode (boolean), notifications (object with boolean flags), and connection (object with host, gpioProfile, and apiUrl string values)
2. WHEN POST /api/settings is called with a JSON body containing one or more of the recognized settings fields (thresholds, autoMode, notifications, connection), THE Backend SHALL use the Settings_Service to merge the provided fields with existing stored settings, persist the result to the Database, and return the complete saved settings object as JSON
3. IF POST /api/settings is called with a request body that is not valid JSON or contains no recognized settings fields, THEN THE Backend SHALL return an error response with HTTP status 400 and a JSON body containing ok set to false and a message indicating the validation failure, without modifying stored settings
4. WHEN the Backend starts and the JSON file at backend/data/settings.json exists with parseable content and the database settings table contains no rows, THE Settings_Service SHALL read all key-value pairs from the JSON file and insert them into the database settings table
5. IF the migration in criterion 4 encounters a malformed JSON file (unparseable content), THEN THE Settings_Service SHALL log a warning, skip the migration, and start with default settings without preventing application startup
6. THE Settings_Service SHALL store the following setting categories with these constraints: automation thresholds (temperature integer 18–42, moisture integer 15–75, light integer 0–1023), auto mode state (boolean), notification preferences (up to 3 boolean flags), and Raspberry Pi connection metadata (host string max 253 characters, gpioProfile string max 10 characters, apiUrl string max 2048 characters)

### Requirement 8: Backend Test Suite

**User Story:** As a system developer, I want automated tests for the backend API and services, so that I can verify correctness and prevent regressions when making changes.

#### Acceptance Criteria

1. THE Backend SHALL include a pytest test suite with tests for all API endpoints (health, sensors, history, status, device control, auth, settings) that verify each endpoint returns the expected HTTP status code (200 for success, 404 for unknown routes, 404 for unknown devices) and a JSON response body containing the documented keys
2. THE Backend test suite SHALL include unit tests for the Device_Controller verifying: manual override blocks auto-source commands for the configured override duration (default 120 seconds), GPIO alias resolution maps aliases (pump, fan, light) to canonical device names (drip, cooler, led), active-low logic outputs GPIO 0 when enabled and 1 when disabled, and concurrent calls from 2 or more threads do not corrupt device state
3. THE Backend test suite SHALL include unit tests for the Sensor_Service verifying: mock data generation produces values within defined ranges (temperature 20.0–32.0 °C, humidity 50–80%, soilMoisture 30–70%, light 80–1000), ADC-to-percent conversion maps the configured dry value (850) to 0% and wet value (350) to 100% with clamping at boundaries, and history_data retains a maximum of 24 entries discarding the oldest when exceeded
4. THE Backend test suite SHALL include unit tests for the Auth_Service verifying: password hashing produces a value that is not equal to the plaintext input, JWT token generation returns a decodable token containing the expected subject claim, token validation rejects tokens signed with an incorrect secret, and token expiration rejects tokens whose expiry time has passed
5. THE Backend test suite SHALL include unit tests for the Settings_Service verifying: threshold values outside the valid numeric range (0 to 100 for percentage-based thresholds) are rejected, read operations return previously written values, and read operations return defined default values when no prior write has occurred
6. WHEN the test suite runs, THE test suite SHALL use mock GPIO and mock sensor libraries (patching RPi.GPIO, Adafruit_DHT, and spidev imports) so tests can execute on any machine without Raspberry Pi hardware
7. IF a device control endpoint receives an unknown device name that is not in the configured device list or alias map, THEN THE Backend SHALL return HTTP 404 with a JSON response containing an ok field set to false and a message field indicating the device is unrecognized
8. WHEN the test suite runs, THE test suite SHALL achieve a minimum of 80% line coverage across the backend package as measured by pytest-cov

### Requirement 9: Frontend Test Suite

**User Story:** As a system developer, I want automated tests for the frontend components and hooks, so that I can verify UI behavior and prevent regressions.

#### Acceptance Criteria

1. THE Frontend SHALL include a vitest test suite with tests for the useSocket hook verifying connection state tracking, disconnect detection, and event handler registration and cleanup
2. THE Frontend test suite SHALL include tests for the AuthContext verifying login stores user and token in localStorage, logout removes them, isAuthenticated reflects current state, and login with invalid credentials (empty email or password shorter than 4 characters) throws an error
3. THE Frontend test suite SHALL include tests for the GreenhouseContext verifying sensor data is fetched on mount, device control calls the API and updates local state, and status data is merged into context
4. THE Frontend test suite SHALL include tests for the API service layer verifying: mock fallback returns local data when VITE_API_URL is not set, token is injected into request headers from localStorage, and network errors fall back to local data in development mode
5. WHEN the test suite runs, THE test suite SHALL mock all network requests using msw or vi.mock and mock WebSocket connections using a socket.io mock so tests execute without a running backend
