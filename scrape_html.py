import os
import csv
from datetime import datetime
import re
from collections import defaultdict
from bs4 import BeautifulSoup

# This format ensures consistency in date naming
DATE_FORMAT = "%Y.%m.%d"
today_date = datetime.today().strftime(DATE_FORMAT)

leetcode_url_prefix = "https://leetcode.com"

# Regex to validate date "YYYY.MM.DD"
def is_valid_date(date_str):
    return re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", date_str) is not None

def extract_problems_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("div", role="row")

    problems = []
    suspicious_rows = []  # For logging rows that don't fit our expectations

    for row in rows:
        # Attempt to find a date
        date_tag = row.find("div", class_="text-sd-muted-foreground")
        extracted_date = date_tag.get_text(strip=True) if date_tag else None

        if extracted_date and is_valid_date(extracted_date):
            date = extracted_date
        else:
            date = today_date  # Fallback if missing or invalid

        # Attempt to find title and problem ID
        title_tag = row.find("a", class_="font-semibold")
        if title_tag:
            full_title = title_tag.get_text(strip=True)
            url_suffix = title_tag.get("href", None)

            # Split off problem ID (e.g. "629. K Inverse Pairs Array")
            if ". " in full_title:
                problem_id, problem_title = full_title.split(". ", 1)
            else:
                # If the format doesn't match ID + title, mark as suspicious
                suspicious_rows.append(f"Title format unexpected: {full_title}")
                problem_id, problem_title = "Unknown", full_title

            # Build the full URL
            if url_suffix:
                full_url = leetcode_url_prefix + url_suffix
            else:
                full_url = None
        else:
            # Missing a main link for problem? Mark row as suspicious
            suspicious_rows.append("No title link found in row")
            problem_id, problem_title, full_url = None, None, None

        # Attempt to find difficulty
        difficulty_container = row.find("div", class_="flex max-w-[300px] flex-col")
        if difficulty_container:
            # Looking for a class that includes both text-[14px] and text-sd-
            difficulty_tag = difficulty_container.find(
                lambda tag: tag.name in ["span", "div"] and
                            tag.has_attr("class") and
                            any("text-[14px]" in c for c in tag["class"]) and
                            any("text-sd-" in c for c in tag["class"])
            )
            difficulty = difficulty_tag.get_text(strip=True) if difficulty_tag else None
            if difficulty == "Med.":
                difficulty = "Medium"
        else:
            difficulty = None

        # Decide if this row looks legitimate
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

# Main driver
def process_leetcode_html_files(input_folder="html", file_pattern="html%02d.txt", output_csv="leetcode_problems.csv"):
    """
    1. Looks in 'input_folder' for HTML files named according to file_pattern.
    2. Extracts problem info from each HTML file.
    3. Deduplicates based on (problem_id, problem_title).
    4. Logs suspicious rows (missing or malformed data).
    5. Writes final results to a CSV.
    """
    all_problems = []
    suspicious_rows_overall = []

    # Extract from each HTML file
    for i in range(1, 11):
        filename = os.path.join(input_folder, file_pattern % i)
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                html_content = f.read()
            problems, suspicious_rows = extract_problems_from_html(html_content)
            all_problems.extend(problems)
            suspicious_rows_overall.extend(suspicious_rows)
        else:
            print(f"File not found: {filename}")

    # Print suspicious rows if any
    if suspicious_rows_overall:
        print(f"Found {len(suspicious_rows_overall)} suspicious row(s). Listing them below:")
        for row_info in suspicious_rows_overall:
            print("  -", row_info)
    else:
        print("No suspicious rows encountered.")

    # Deduplicate by (problem_id, problem_title)
    # If the same (id, title) appears, we count it as a duplicate
    # and keep only the first one we encountered
    seen = {}
    duplicates = defaultdict(int)

    for p in all_problems:
        key = (p["problem_id"], p["problem_title"])
        if key not in seen:
            seen[key] = p
        else:
            duplicates[key] += 1

    # Print duplicates
    if duplicates:
        print(f"Found {len(duplicates)} duplicate problem(s). Details:")
        for key, count in duplicates.items():
            print(f"  - Problem: {key} repeated {count+1} times")
    else:
        print("No duplicates detected.")

    # Rebuild the list of unique problems
    unique_problems = list(seen.values())

    # Write to CSV
    csv_columns = ["date", "problem_id", "problem_title", "difficulty", "url"]
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(unique_problems)

    print(f"\nFinished. CSV file '{output_csv}' has been created with {len(unique_problems)} unique problem(s).")

# Example call if you want to run it directly:
if __name__ == "__main__":
    process_leetcode_html_files()
