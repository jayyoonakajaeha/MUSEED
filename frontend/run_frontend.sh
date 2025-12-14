#!/bin/bash
# MUSEED Frontend Production Start Script

cd "$(dirname "$0")"

echo "Starting MUSEED Frontend in Production Mode..."
npm start -- -p 3000
