from fastapi import FastAPI
from pymongo import MongoClient
from bson import ObjectId
# ADD THIS IMPORT
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
connection_string = os.environ.get("CONNECTION_STRING")
try:
    client = MongoClient(connection_string)
except Exception as e:
    print(e)

notes_collection = client["sample_mflix"]["notes"]

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

# @app.get("/notes")
# def get_notes():
#     return fake_notes_db

@app.get("/notes")
def get_notes():
    # Look for all notes in collection
    notes = list(notes_collection.find())
    if not notes:
        return []
    
    # Make sure ids are strings
    formatted = []
    for note in notes:
        formatted.append({
            "id_": str(note["_id"]),
            "text": note.get("text", "")
        })
    return formatted

# @app.get("/notes/{note_id}")
# def get_note(note_id: int):
#     for note in fake_notes_db:
#         if note["id"] == note_id:
#             return note
#     return {"message": "Note not found"}

@app.get("/notes/{note_id}")
def get_note(note_id: str):
    note = notes_collection.find_one({"_id": ObjectId(note_id)})
    if note:
        return {"id_": str(note["_id"]), "text": note.get("text", "")}
    return {"message": "Note not found"}

from pydantic import BaseModel

class NoteCreate(BaseModel):
    text: str

# @app.post("/notes")
# def create_note(note: NoteCreate):
#     # Generate a new ID (simple approach for demo)
#     new_id = max([n["id"] for n in fake_notes_db], default=0) + 1
#     new_note = {"id": new_id, "text": note.text}
#     fake_notes_db.append(new_note)
#     return new_note

@app.post("/notes")
def create_note(note: NoteCreate):
    # Generate a new ID (simple approach for demo)
    note_id = notes_collection.insert_one({"text": note.text}).inserted_id
    return {"id_": str(note_id), "text": note.text}

# @app.delete("/notes/{note_id}")
# def delete_note(note_id: int):
#     global fake_notes_db
#     for i, note in enumerate(fake_notes_db):
#         if note["id"] == note_id:
#             deleted_note = fake_notes_db.pop(i)
#             return {"message": f"Note with id {note_id} has been deleted", "deleted_note": deleted_note}
#     return {"message": "Note not found"}

@app.delete("/notes/{note_id}")
def delete_note(note_id: str):
    obj_id = ObjectId(note_id)
    deleted_note = notes_collection.find_one({"_id": obj_id})
    num_removed = notes_collection.delete_one({"_id": obj_id}).deleted_count

    if num_removed == 1:
        return {"message": f"Note with id {note_id} has been deleted", "deleted_note": deleted_note.get("text", "")}
    return {"message": "Note not found"}