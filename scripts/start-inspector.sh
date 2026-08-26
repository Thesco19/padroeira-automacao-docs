#!/bin/bash
ALLOWED_ORIGINS="http://10.0.1.95:6274,http://localhost:6274,http://127.0.0.1:6274" HOST=0.0.0.0 npx @modelcontextprotocol/inspector http://localhost:8765/sse
