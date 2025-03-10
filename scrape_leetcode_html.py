import os
import csv
from datetime import datetime
import re
from collections import defaultdict
from bs4 import BeautifulSoup

date_format = r"%Y.%m.%d"
today_date = datetime.today().strftime(date_format)

leetcode_url_prefix = "https://leetcode.com"

# Regex to validate date "YYYY.MM.DD"
def is_valid_date(date_str):
    return re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", date_str) is not None

def get_row_date(row):
    date_tag = row.find("div", class_="text-sd-muted-foreground")
    if (date_tag and
        date_tag.get_text(strip=True) and
        is_valid_date(date_tag.get_text(strip=True))):
        date = date_tag.get_text(strip=True)
    else:
        date = today_date
    return date

def extract_problems_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("div", role="row")

    problems = []
    suspicious_rows = []

    for row in rows:
        # Attempt to find a date
        date = get_row_date(row)
        
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

        # Attempted to find "last result"
        last_result_container = row.find("div", class_="text-sd-muted-foreground flex h-full items-center")
        if last_result_container:
            last_result_tag = last_result_container.get_text(strip=True)
        else:
            last_result_tag = None
        if last_result_tag != 'Accepted':
            print(f'problem id {problem_id} has last result tag: {last_result_tag}')
        

        # Check if we have enough data to consider this a valid problem
        if all([problem_id, problem_title, full_url, difficulty]):
            problems.append({
                "date": date,
                "problem_id": problem_id,
                "problem_title": problem_title,
                "difficulty": difficulty,
                "last_result": last_result_tag,
                "url": full_url,
            })
        else:
            row_text = row.get_text(strip=True)
            suspicious_rows.append(
                f"Missing fields: {problem_id}, {problem_title}, {difficulty}, {full_url}. "
                f"Raw text: {row_text[:200]}"
            )

    return problems, suspicious_rows

def process_leetcode_html_files(
    # input_folder="html",
    input_folder="scratch",
    output_csv="leetcode_problems.csv",
    pattern_mode=None  # <--- NEW parameter
):
    """
    1. Looks in 'input_folder' for all relevant files.
    2. Extracts problem info from each file.
    3. Deduplicates based on (problem_id, problem_title).
    4. Logs suspicious rows.
    5. Writes final results to a CSV.

    :param pattern_mode: can be None, 'number', or 'progress' (or anything else you define)
    """

    if not os.path.isdir(input_folder):
        print(f"ERROR: {input_folder} is not a valid directory.")
        return

    # Gather all filenames first
    all_files = os.listdir(input_folder)

    # Depending on pattern_mode, filter which files we consider
    if pattern_mode == "number":
        # e.g. only files starting with a digit
        html_files = [
            f for f in all_files
            if f.endswith(".html") and re.match(r"^\d", f)
        ]
    elif pattern_mode == "progress":
        # e.g. only files starting with 'Progress'
        html_files = [
            f for f in all_files
            if f.endswith(".html") and f.startswith("Progress")
        ]
    else:
        # Default: gather all .html or .txt files
        html_files = [
            f for f in all_files
            if f.endswith(".html") or f.endswith(".txt")
        ]

    all_problems = []
    suspicious_rows_overall = []

    for file_name in html_files:
        file_path = os.path.join(input_folder, file_name)
        print(f"[DEBUG] Processing file: {file_path} ...")
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        problems, suspicious_rows = extract_problems_from_html(html_content)
        print(f"  [DEBUG] {file_name}: Extracted {len(problems)} problems")
        all_problems.extend(problems)
        suspicious_rows_overall.extend(suspicious_rows)


    # Deduplicate
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

    # Write CSV
    csv_columns = ["date", "problem_id", "problem_title", "difficulty", "last_result", "url"]
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(unique_problems)

    print(f"\n[DEBUG] Finished. CSV file '{output_csv}' has {len(unique_problems)} unique problem(s).")

if __name__ == "__main__":
    # Example usage:
    # process_leetcode_html_files(pattern_mode=None)  # to get all .html/.txt
    # process_leetcode_html_files(pattern_mode="number")    # files starting with a digit
    process_leetcode_html_files(pattern_mode="progress")  # files starting with 'Progress'
    # process_leetcode_html_files()