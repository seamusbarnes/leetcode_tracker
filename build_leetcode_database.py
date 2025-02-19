import json
import os
from datetime import datetime
from dateutil import parser  # For flexible date parsing

CONFIG = {
    'JSON_FILE': 'leetcode_progress.json',
    'SOLUTIONS_DIR': 'solutions'
}

os.makedirs(CONFIG['SOLUTIONS_DIR'], exist_ok=True)

def load_progress():
    """Load problem progress from JSON file."""
    if os.path.exists(CONFIG['JSON_FILE']):
        with open(CONFIG['JSON_FILE'], 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_progress(progress):
    """Save the updated progress list to JSON file."""
    with open(CONFIG['JSON_FILE'], 'w') as f:
        json.dump(progress, f, indent=4)

def parse_date(date_input):
    """Convert various date formats into YYYY-MM-DD format."""
    if not date_input.strip():
        return None  # Keep existing value if input is empty
    try:
        parsed_date = parser.parse(date_input, dayfirst=True)  # Handles multiple formats
        return parsed_date.strftime("%Y-%m-%d")  # Standardize to YYYY-MM-DD
    except ValueError:
        print("⚠️ Invalid date format. Please try again.")
        return None

def add_or_update_problem():
    """Prompt user to add or update a LeetCode problem entry."""
    progress = load_progress()

    problem_number = input("Problem Number (e.g., 1, 2, 3): ").strip()

    # Check if the problem already exists
    existing_entry = next((p for p in progress if p["problem_number"] == problem_number), None)

    if existing_entry:
        print(f"🔄 Updating existing problem: {existing_entry['title']} ({problem_number})")
    else:
        print("🆕 Adding a new problem entry.")
        existing_entry = {}  # Create an empty entry for a new problem

    # Get user input, keeping existing values if input is empty
    title = input(f"Problem Title [{existing_entry.get('title', '')}]: ").strip() or existing_entry.get("title", "")
    difficulty = input(f"Difficulty (Easy/Medium/Hard) [{existing_entry.get('difficulty', '')}]: ").strip().capitalize() or existing_entry.get("difficulty", "")
    leetcode_url = input(f"LeetCode URL [{existing_entry.get('leetcode_url', '')}]: ").strip() or existing_entry.get("leetcode_url", "")
    neetcode_url = input(f"NeetCode Video URL (optional) [{existing_entry.get('neetcode_url', '')}]: ").strip() or existing_entry.get("neetcode_url", None)
    
    tags = input(f"Tags (comma-separated) [{', '.join(existing_entry.get('tags', []))}]: ").strip()
    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else existing_entry.get("tags", [])

    # Ask for first submission date and keep the existing one if blank
    while True:
        first_submission_date = input(f"First Submission Date (e.g., 'May 21, 2023' or '21/05/2023') [{existing_entry.get('first_submission_date', '')}]: ").strip()
        formatted_date = parse_date(first_submission_date) if first_submission_date else existing_entry.get("first_submission_date", "")
        if formatted_date:
            break

    # Create the updated entry
    entry = {
        "problem_number": problem_number,
        "title": title,
        "difficulty": difficulty,
        "leetcode_url": leetcode_url,
        "neetcode_url": neetcode_url,
        "tags": tags_list,
        "first_submission_date": formatted_date
    }

    # Replace or add the entry
    if existing_entry in progress:
        progress[progress.index(existing_entry)] = entry
    else:
        progress.append(entry)

    save_progress(progress)
    print(f"✅ Problem {problem_number} - '{title}' saved!")

if __name__ == "__main__":
    while True:
        print("\nLeetCode Progress Tracker")
        print("1. Add or update a problem")
        print("2. View progress")
        print("3. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            add_or_update_problem()
        elif choice == "2":
            progress_data = load_progress()
            print(json.dumps(progress_data, indent=4))  # Pretty print progress
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")
