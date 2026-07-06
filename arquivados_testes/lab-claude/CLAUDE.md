# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Common Commands

- **Start the server**:
  ```bash
  npm start
  ```
  To specify a custom port:
  ```bash
  PORT=8080 npm start
  ```

- **Run the proxy**:
  ```bash
  ./start_proxy.sh
  ```

- **Run Claude Code**:
  ```bash
  ./run_claude.sh
  ```

## Architecture

### High-Level Architecture

The project consists of a simple HTTP server implemented using Node.js's native `http` module. The server handles GET requests to the root URL (`/`) and responds with a welcome message. Any other route or method results in a 404 Not Found response.

### Key Components

1. **Server Implementation (`index.js`)**:
   - The server is created using the `http` module.
   - It listens on a port specified by the `PORT` environment variable or defaults to port 3000.
   - It handles GET requests to the root URL and responds with a welcome message.
   - Any other route or method results in a 404 Not Found response.

2. **Configuration Files**:
   - `package.json`: Contains metadata and scripts for the project.
   - `run_claude.sh`: Script to run Claude Code with specific configurations.
   - `start_proxy.sh`: Script to start the proxy server.

### Environment Variables

- `PORT`: Specifies the port on which the server will listen. If not specified, it defaults to 3000.
- `ANTHROPIC_BASE_URL`: URL for the Anthropic API proxy.
- `ANTHROPIC_AUTH_TOKEN`: Authentication token for the Anthropic API.
- `ANTHROPIC_MODEL`: Specifies the model to be used by Claude Code.
- `ENABLE_TOOL_SEARCH`: Enables tool search functionality.

### Running the Project

1. **Start the Proxy Server**:
   ```bash
   ./start_proxy.sh
   ```

2. **Run Claude Code**:
   ```bash
   ./run_claude.sh
   ```

3. **Start the HTTP Server**:
   ```bash
   npm start
   ```
   To specify a custom port:
   ```bash
   PORT=8080 npm start
   ```

4. **Access the Server**:
   Open a web browser and navigate to `http://localhost:3000` (or the specified port).

## Additional Notes

- The project uses Node.js version 18 or higher.
- The server is implemented using the native `http` module, ensuring simplicity and minimal dependencies.
- The proxy server is configured to use LiteLLM and runs on port 8000.
- Claude Code is configured to use the Mistral model by default, but other models can be selected by uncommenting the appropriate line in `run_claude.sh`.