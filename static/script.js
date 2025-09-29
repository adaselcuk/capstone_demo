// --- CONFIGURATION ---
// Set this to your FastAPI backend URL.
// If you are running the uvicorn server with SSL, it will be https://localhost:8443
// If you are running the uvicorn server without SSL, it will be http://localhost:8000
const API_BASE_URL = "https://localhost:8443";

// --- DOM ELEMENTS ---
const notesList = document.getElementById('notes-list');
const noteForm = document.getElementById('note-form');
const noteTextInput = document.getElementById('note-text');
const errorMessageDiv = document.getElementById('error-message');
const loadingIndicator = document.getElementById('loading-indicator');

// --- FUNCTIONS ---

/**
 * Displays an error message to the user.
 * @param {string} message The error message to display.
 */
function displayError(message) {
    errorMessageDiv.textContent = message;
    errorMessageDiv.style.display = 'block';
}

/**
 * Hides the error message.
 */
function clearError() {
    errorMessageDiv.textContent = '';
    errorMessageDiv.style.display = 'none';
}

/**
 * Renders the list of notes to the page.
 * @param {Array<Object>} notes - An array of note objects, e.g., [{id: 1, text: 'My first note'}]
 */
function renderNotes(notes) {
    notesList.innerHTML = ''; // Clear existing notes
    if (notes.length === 0) {
        notesList.innerHTML = '<li>No notes yet. Add one!</li>';
        return;
    }
    notes.forEach(note => {
        const li = document.createElement('li');
        li.dataset.id = note.id;

        const span = document.createElement('span');
        span.className = 'note-text';
        span.textContent = note.text;

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.textContent = 'Delete';
        
        deleteBtn.addEventListener('click', async () => {
            await deleteNote(note.id);
        });

        li.appendChild(span);
        li.appendChild(deleteBtn);
        notesList.appendChild(li);
    });
}

/**
 * Fetches all notes from the backend and renders them.
 */
async function getAndRenderNotes() {
    clearError();
    loadingIndicator.style.display = 'block';
    notesList.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE_URL}/notes`);
        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}. Could not fetch notes.`);
        }
        const notes = await response.json();
        renderNotes(notes);
    } catch (error) {
        displayError(error.message);
        notesList.innerHTML = '<li>Could not load notes.</li>';
    } finally {
        loadingIndicator.style.display = 'none';
    }
}

/**
 * Creates a new note by sending a POST request to the backend.
 * @param {string} text - The content of the note.
 */
async function createNote(text) {
    clearError();
    try {
        const response = await fetch(`${API_BASE_URL}/notes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text }),
        });

        if (response.status === 422) {
            const errorData = await response.json();
            throw new Error(`Validation Error: ${errorData.detail[0].msg}`);
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Server error: ${response.status}`);
        }

        // After creating a note, refresh the list to show the new one
        await getAndRenderNotes();
    } catch (error) {
        displayError(error.message);
    }
}

/**
 * Deletes a note by its ID.
 * @param {number} noteId - The ID of the note to delete.
 */
async function deleteNote(noteId) {
    clearError();
    try {
        const response = await fetch(`${API_BASE_URL}/notes/${noteId}`, {
            method: 'DELETE',
        });
        
        if (!response.ok) {
             const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Failed to delete note: ${response.status}`);
        }

        // After deleting, refresh the notes list
        await getAndRenderNotes();

    } catch (error) {
        displayError(error.message);
    }
}

// --- EVENT LISTENERS ---

// Add event listener for form submission to create a new note
noteForm.addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevent default form submission
    const noteText = noteTextInput.value.trim();
    
    if (noteText) {
        await createNote(noteText);
        noteTextInput.value = ''; // Clear the input field
        noteTextInput.focus();
    }
});

// Initial load of notes when the script runs
document.addEventListener('DOMContentLoaded', getAndRenderNotes);
