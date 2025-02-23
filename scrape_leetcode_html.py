import os
import csv
from datetime import datetime
import re
from collections import defaultdict
from bs4 import BeautifulSoup

DATE_FORMAT = "%Y.%m.%d"
today_date = datetime.today().strftime(DATE_FORMAT)

leetcode_url_prefix = "https://leetcode.com"

# Regex to validate date "YYYY.MM.DD"
def is_valid_date(date_str):
    return re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", date_str) is not None

def extract_problems_from_html(html, debug_file=""):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("div", role="row")

    print(f"  [DEBUG] {debug_file}: Found {len(rows)} rows (div[role='row'])")

    problems = []
    suspicious_rows = []

    for row in rows:
        # Attempt to find a date
        date_tag = row.find("div", class_="text-sd-muted-foreground")
        extracted_date = date_tag.get_text(strip=True) if date_tag else None

        if extracted_date and is_valid_date(extracted_date):
            date = extracted_date
        else:
            date = today_date  # fallback

        # Attempt to find title and problem ID
        # title_tag = row.find("a", class_="font-semibold")
        # if title_tag:
        #     full_title = title_tag.get_text(strip=True)
        #     url_suffix = title_tag.get("href", None)

        #     if ". " in full_title:
        #         problem_id, problem_title = full_title.split(". ", 1)
        #     else:
        #         suspicious_rows.append(f"Title format unexpected: {full_title}")
        #         problem_id, problem_title = "Unknown", full_title

        #     if url_suffix:
        #         full_url = leetcode_url_prefix + url_suffix
        #     else:
        #         full_url = None
        # else:
        #     suspicious_rows.append("No title link found in row")
        #     problem_id, problem_title, full_url = None, None, None

        # Attempt to find title and problem ID
        title_tag = row.find("a", class_="font-semibold")
        if title_tag:
            # Get raw text and normalise any weird spacing
            raw_title = title_tag.get_text(strip=True)
            full_title = re.sub(r"\s+", " ", raw_title).strip()

            url_suffix = title_tag.get("href", None)

            # Attempt to parse out the problem ID based on "X. Title"
            if ". " in full_title:
                problem_id, problem_title = full_title.split(". ", 1)
            else:
                suspicious_rows.append(f"Title format unexpected: {full_title}")
                problem_id, problem_title = "Unknown", full_title

            if url_suffix:
                full_url = leetcode_url_prefix + url_suffix
            else:
                full_url = None
        else:
            suspicious_rows.append("No title link found in row")
            problem_id, problem_title, full_url = None, None, None

        # Attempt to find difficulty
        difficulty_container = row.find("div", class_="flex max-w-[300px] flex-col")
        if difficulty_container:
            difficulty_tag = difficulty_container.find(
                lambda tag: (
                    tag.name in ["span", "div"]
                    and tag.has_attr("class")
                    and any("text-[14px]" in c for c in tag["class"])
                    and any("text-sd-" in c for c in tag["class"])
                )
            )
            difficulty = difficulty_tag.get_text(strip=True) if difficulty_tag else None
            # Convert "Med." to "Medium"
            if difficulty == "Med.":
                difficulty = "Medium"
        else:
            difficulty = None

        # Check if we have enough data to consider this a valid problem
        if all([problem_id, problem_title, full_url, difficulty]):
            problems.append({
                "date": date,
                "problem_id": problem_id,
                "problem_title": problem_title,
                "difficulty": difficulty,
                "url": full_url,
            })
        else:
            row_text = row.get_text(strip=True)
            suspicious_rows.append(
                f"Missing fields: {problem_id}, {problem_title}, {difficulty}, {full_url}. "
                f"Raw text: {row_text[:200]}"
            )

    return problems, suspicious_rows

def process_leetcode_html_files(input_folder="html02", output_csv="leetcode_problems.csv"):
    """
    1. Looks in 'input_folder' for all .html files.
    2. Extracts problem info from each file.
    3. Deduplicates based on (problem_id, problem_title).
    4. Logs suspicious rows.
    5. Writes final results to a CSV.
    """
    print(f"[DEBUG] Scanning folder: {input_folder}")
    if not os.path.isdir(input_folder):
        print(f"ERROR: {input_folder} is not a valid directory.")
        return

    # Gather all .html files in the given folder
    html_files = [
        f for f in os.listdir(input_folder)
        if f.endswith(".html") or f.endswith(".txt")
    ]
    print(f"[DEBUG] Found {len(html_files)} .html files:", html_files)

    all_problems = []
    suspicious_rows_overall = []

    for file_name in html_files:
        file_path = os.path.join(input_folder, file_name)
        print(f"[DEBUG] Processing file: {file_path} ...")
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Pass in file_name as debug info
        problems, suspicious_rows = extract_problems_from_html(html_content, debug_file=file_name)
        print(f"  [DEBUG] {file_name}: Extracted {len(problems)} problems")
        all_problems.extend(problems)
        suspicious_rows_overall.extend(suspicious_rows)

    # Print suspicious rows if any
    if suspicious_rows_overall:
        print(f"\n[DEBUG] Found {len(suspicious_rows_overall)} suspicious row(s):")
        for row_info in suspicious_rows_overall:
            print("  -", row_info)
    else:
        print("\n[DEBUG] No suspicious rows encountered.")

    # Deduplicate by (problem_id, problem_title)
    seen = {}
    duplicates = defaultdict(int)

    for p in all_problems:
        key = (p["problem_id"], p["problem_title"])
        if key not in seen:
            seen[key] = p
        else:
            duplicates[key] += 1

    if duplicates:
        print(f"[DEBUG] Found {len(duplicates)} duplicate problem(s). Details:")
        for key, count in duplicates.items():
            print(f"  - Problem: {key} repeated {count + 1} times")
    else:
        print("[DEBUG] No duplicates detected.")

    unique_problems = list(seen.values())

    # Write to CSV
    csv_columns = ["date", "problem_id", "problem_title", "difficulty", "url"]
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(unique_problems)

    print(f"\n[DEBUG] Finished. CSV file '{output_csv}' has been created with {len(unique_problems)} unique problem(s).")

if __name__ == "__main__":
    process_leetcode_html_files()
