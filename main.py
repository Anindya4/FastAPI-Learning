from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def hello():
    return {"message" : "Hello from my first FastAPI 😉"}

@app.get('/about')
def about():
    return {"message" : "This is me Aninyda a CS student 👩‍💻 also a hardworking dreamer"}