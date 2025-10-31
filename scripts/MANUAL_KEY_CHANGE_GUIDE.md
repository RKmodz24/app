# Manual Key Change Guide (Backend App Key + Special Function)

Location of the key (code constant):
- File: /app/backend/server.py
- Search for: `APP_KEY = "123456"`

How to change the key:
1. Open /app/backend/server.py in your editor.
2. Find the constant line:
   APP_KEY = "123456"
3. Replace 123456 with your new key. Example:
   APP_KEY = "my-new-secure-key"
4. Save the file.
5. Restart only the backend service:
   sudo supervisorctl restart backend

What changes automatically:
- The validation endpoint (/api/key/validate) will accept only the new key.
- The Special activation trigger uses the same APP_KEY automatically. No extra change needed.

APIs for verification (use curl):
- Validate key:
  curl -s -X POST $REACT_APP_BACKEND_URL/api/key/validate -H 'Content-Type: application/json' -d '{"key":"my-new-secure-key"}'
- Activate special function:
  curl -s -X POST $REACT_APP_BACKEND_URL/api/special/activate -H 'Content-Type: application/json' -d '{"key":"my-new-secure-key"}'

Notes:
- Do not edit any .env URL/port variables.
- If MongoDB is used, the change does not affect DB.
- Never commit real secret keys to public repositories.
