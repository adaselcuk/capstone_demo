from fastapi import FastAPI
# ADD THIS IMPORT
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"] # This allows any origin

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Notes App API"}

# Let's create some fake in-memory data for our notes
fake_notes_db = [
    {"id": 1, "text": "First note from the backend!"},
    {"id": 2, "text": "Learn how to connect a frontend."},
]

@app.get("/notes")
def get_notes():
    return fake_notes_db

@app.get("/notes/{note_id}")
def get_note(note_id: int):
    for note in fake_notes_db:
        if note["id"] == note_id:
            return note
    return {"message": "Note not found"}

from pydantic import BaseModel

class NoteCreate(BaseModel):
    text: str

@app.post("/notes")
def create_note(note: NoteCreate):
    # Generate a new ID (simple approach for demo)
    new_id = max([n["id"] for n in fake_notes_db], default=0) + 1
    new_note = {"id": new_id, "text": note.text}
    fake_notes_db.append(new_note)
    return new_note

@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    global fake_notes_db
    for i, note in enumerate(fake_notes_db):
        if note["id"] == note_id:
            deleted_note = fake_notes_db.pop(i)
            return {"message": f"Note with id {note_id} has been deleted", "deleted_note": deleted_note}
    return {"message": "Note not found"}
