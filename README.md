
- Frontend: JavaScript (placeholder)
- Backend: Python (placeholder)

OUR STRUCTURE: 
- frontend/ — JS placeholder
- backend/  — Python placeholder
- docs/     — notes, design, API drafts

WORKFLOW:
- Default branch: main
- Use feature branches: feat/*, fix/*, chore/*
- Merge via Pull Requests to main

FLEXING:
- Allowed

BUILD TOOLS:
    - Browserify in order to bundle app.js and appLogic.cjs:
        - (Initialize package.json, skip step if package.json already exists) npm init -y
        - (Install broswerify) npm install browserify --save-dev
        - (app_bundle.js must be built everytime app.js or appLogic.cjs are altered, is relative to backend/static) npx browserify app.js -o app_bundle.js