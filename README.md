
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
        - (Build command, both paths must be relative to backend/static) npx browserify app.js -o app_bundle.js