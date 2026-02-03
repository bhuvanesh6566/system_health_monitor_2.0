# AIOps Monitor – React Frontend

Run the **API from the project root** first, then start the frontend from here.

## From project root (first terminal)

```bash
cd "c:\Users\asus\OneDrive\Desktop\react mini"
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

Keep this running. Do **not** run `uvicorn` from inside the `frontend` folder — `api.py` lives in the parent directory.

## From this folder (second terminal)

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173
