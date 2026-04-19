from fastapi import FastAPI

app = FastAPI(title='Habit Tracker API')

@app.get("/")
def root():
    return {"message": "Привет, трекер привычек!"}

@app.get("/health")
def health():
    return {"status": "ok"}
