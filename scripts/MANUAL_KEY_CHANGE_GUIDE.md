# Manual Guide: App Key Change (Step-by-Step)

Yeh guide aapko backend key (APP_KEY) manually change karne ke liye step-by-step instructions deta hai. Is key se:
- `/api/key/validate` par key verify hoti hai
- `/api/special/activate` par "special function" activate hota hai

Current default key: `123456`
Key kahan hai: `/app/backend/server.py` file mein `APP_KEY` constant ke roop mein.

---------------------------------
## 1) Key location identify karein
- File path: `/app/backend/server.py`
- Search keyword: `APP_KEY = "123456"`

Example snippet:
```py
# App Key (CODE CONSTANT as requested)
# Manually change this value to update the app key.
# Default per requirement: "123456"
APP_KEY = "123456"
```

---------------------------------
## 2) Key ko change karna (manual edit)
1. Editor me `/app/backend/server.py` kholein
2. Line (snippet ke paas) par value badlein. Example:
   - Purana: `APP_KEY = "123456"`
   - Naya: `APP_KEY = "my-new-secure-key"`
3. File save karein

Note:
- Special function ka trigger key `APP_KEY` se linked hai (code me `SPECIAL_TRIGGER_KEY = APP_KEY`).
- Iska matlab: aap jaisi key change karenge, `special/activate` ke liye wahi nayi key lagegi. Alag se kuch change karne ki zarurat nahi.

---------------------------------
## 3) Backend restart (zaroori)
- Command:
```
sudo supervisorctl restart backend
```
- Restart ke baad backend hot-reload ke saath nayi key load kar lega.

Logs dekhne ke liye (agar error aaye):
```
tail -n 100 /var/log/supervisor/backend.err.log
```
Aur normal logs:
```
tail -n 100 /var/log/supervisor/backend.out.log
```

---------------------------------
## 4) Verify karein (curl examples)
A) Local (container ke andar) direct port se:
```
# Special function activation (success hona chahiye jab sahi key bhejoge)
curl -s -X POST http://127.0.0.1:8001/api/special/activate \
  -H 'Content-Type: application/json' \
  -d '{"key":"my-new-secure-key"}'

# Key validate (true/false return karta hai)
curl -s -X POST http://127.0.0.1:8001/api/key/validate \
  -H 'Content-Type: application/json' \
  -d '{"key":"my-new-secure-key"}'
```

B) Frontend/External URL ke through (Ingress ke via):
- REACT_APP_BACKEND_URL env ka istemaal karein (hardcode mat karein).
```
# Example (shell me var set ho to):
curl -s -X POST "$REACT_APP_BACKEND_URL/api/special/activate" \
  -H 'Content-Type: application/json' \
  -d '{"key":"my-new-secure-key"}'

curl -s -X POST "$REACT_APP_BACKEND_URL/api/key/validate" \
  -H 'Content-Type: application/json' \
  -d '{"key":"my-new-secure-key"}'
```

---------------------------------
## 5) Common FAQs
- Q: Kya `.env` me kuch change karna hai?
  - A: Nahi. Key code constant ke through manage hoti hai. `.env` sirf DB/URLs ke liye hai.
- Q: Special function ka trigger alag key se chalana hai to?
  - A: Bas `APP_KEY` badal dein. Code me `SPECIAL_TRIGGER_KEY = APP_KEY` set hai.
- Q: Purani key `5HxBGMIOWNERSxdms6rpeuht` ka kya?
  - A: System ab uska use nahi karta. Ab sirf `APP_KEY` hi source of truth hai.
- Q: Revert karna ho to?
  - A: `APP_KEY = "123456"` set karke backend restart kar dein.

---------------------------------
## 6) API Reference (quick)
- Validate key:
  - Method/Path: `POST /api/key/validate`
  - Body: `{ "key": "<your-key>" }`
  - Response: `{ "valid": true|false }`

- Special activate:
  - Method/Path: `POST /api/special/activate`
  - Body: `{ "key": "<your-key>" }`
  - Response: `{ "active": true|false, "message": "..." }`

- Special info:
  - Method/Path: `GET /api/special`
  - Response: activation instructions

---------------------------------
## 7) Security tips
- Production me strong, random key use karein.
- Secrets ko public repos me commit na karein.
- Access minimum rakhein aur team me limited logon ko key dikhayein.

Agar aap chahen to main is guide ke basis par frontend par ek simple "Key Tester" screen bhi add kar sakta hoon jisse aap UI se validate/activate check kar paayenge. Bata dijiye.
