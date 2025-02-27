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

def extract_problems_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("div", role="row")

    problems = []
    suspicious_rows = []

    for row in rows:
        # Attempt to find a date
        original_tag = row.find("div", class_="text-sd-muted-foreground")
        print(original_tag)
        # original_extracted = original_tag.get_text(strip=True) if original_extracted else None
        # if original_extracted:
        #     print(original_extracted)


        date_tag = row.find("div", class_="text-sd-muted-foreground")
        extracted_date = date_tag.get_text(strip=True) if date_tag else None

        if extracted_date and is_valid_date(extracted_date):
            date = extracted_date
        else:
            date = today_date  # fallback

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

    # Print any suspicious rows
    # if suspicious_rows_overall:
    #     print(f"\n[DEBUG] Found {len(suspicious_rows_overall)} suspicious row(s):")
    #     for row_info in suspicious_rows_overall:
    #         print("  -", row_info)
    # else:
    #     print("\n[DEBUG] No suspicious rows encountered.")

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

import re
from bs4 import BeautifulSoup

DATE_PATTERN = re.compile(r'^\d{4}\.\d{2}\.\d{2}$')  # e.g. "2024.01.18"

def parse_leetcode_progress(html):
    soup = BeautifulSoup(html, "html.parser")
    # Each top-level problem “row” has class like "odd:bg-sd-card even:bg-sd-accent"
    # or "dark:odd:bg-sd-card dark:even:bg-sd-accent" etc. They also typically have
    # a "flex flex-col" with role="row". We'll look for them by role="row" plus some
    # top-level styling class so we skip sub-rows.
    # A practical approach is:
    top_level_rows = soup.select('div[role="row"].flex.flex-col')

    all_problems = []

    for top_row in top_level_rows:
        # 1) Extract the top-row date (may be e.g. “Yesterday” or “2025.02.25”)
        #    This is in a <div style="width: 150px;"> inside the top-row’s child.
        #    The class is "text-sd-muted-foreground".
        #    We’ll just read the text; if it matches YYYY.MM.DD, we store it, else store raw string.
        date_div = top_row.select_one('div[role="cell"][style*="width: 150px;"] div.text-sd-muted-foreground')
        if date_div:
            raw_top_date = date_div.get_text(strip=True)
            if DATE_PATTERN.match(raw_top_date):
                top_level_date = raw_top_date
            else:
                top_level_date = raw_top_date  # e.g. "Yesterday", "2 days ago", etc.
        else:
            top_level_date = None

        # 2) Extract the problem title link & difficulty
        link_tag = top_row.select_one('a.font-semibold[href^="/problems/"]')
        if not link_tag:
            # If no link, this may be just a “submission sub-row” rather than a main row, skip
            continue

        problem_url = link_tag['href']  # e.g. "/problems/binary-tree-inorder-traversal/"
        problem_title_full = link_tag.get_text(strip=True)
        # Usually "94. Binary Tree Inorder Traversal", so split:
        if '. ' in problem_title_full:
            problem_id, problem_title = problem_title_full.split('. ', 1)
        else:
            # Unexpected format
            problem_id = None
            problem_title = problem_title_full

        # Difficulty is in the sibling <div class="text-[14px] text-sd-???"> (e.g. text-sd-easy)
        # A simpler way is to select the next <div> with text-sd-??? in class:
        difficulty_div = top_row.select_one('div.text-sd-easy, div.text-sd-medium, div.text-sd-hard')
        difficulty = difficulty_div.get_text(strip=True) if difficulty_div else None

        # 3) Extract the sub-table for submissions (if any). It's typically a <div role="table"> inside
        #    the last <div> of the top-level row. Then each submission is a <div role="row"> inside that.
        submissions_table = top_row.select_one('div[role="table"]')
        submissions = []
        if submissions_table:
            # Each submission is a row: <div role="row" class="flex cursor-pointer flex-col">
            submission_rows = submissions_table.select('div[role="row"].flex.cursor-pointer.flex-col')
            for srow in submission_rows:
                # Each submission row has a set of <div role="cell"> for date, result, language, runtime, memory
                # Let’s extract them:
                cells = srow.select('div[role="cell"]')
                # You can also pick them out by the style widths or the text-sd-muted-foreground class, etc.
                if len(cells) < 5:
                    continue  # skip if it doesn't look like a submission row

                # The first cell is the date: e.g. "2025.02.25"
                sub_date_div = cells[0].select_one('.text-sd-muted-foreground')
                submission_date = sub_date_div.get_text(strip=True) if sub_date_div else None

                # The second cell is the result: e.g. "Accepted" or "Runtime Error"
                result_div = cells[1]
                submission_result = result_div.get_text(strip=True) if result_div else None

                # The third cell is the language: e.g. "Python3"
                lang_div = cells[2].select_one('.text-sd-muted-foreground')
                submission_lang = lang_div.get_text(strip=True) if lang_div else None

                # The fourth is runtime, the fifth is memory. They have “text-sd-muted-foreground flex ...”
                runtime_div = cells[3].select_one('.text-sd-muted-foreground')
                submission_runtime = runtime_div.get_text(strip=True) if runtime_div else None

                memory_div = cells[4].select_one('.text-sd-muted-foreground')
                submission_memory = memory_div.get_text(strip=True) if memory_div else None

                submissions.append({
                    'submission_date': submission_date,
                    'result': submission_result,
                    'language': submission_lang,
                    'runtime': submission_runtime,
                    'memory': submission_memory
                })

        # 4) Collect the problem info + the submissions list
        one_problem = {
            'problem_id': problem_id,
            'problem_title': problem_title,
            'problem_url': problem_url,
            'top_row_date': top_level_date,
            'difficulty': difficulty,
            'submissions': submissions
        }
        all_problems.append(one_problem)

    return all_problems


def demo_parsing(html):
    problems = parse_leetcode_progress(html)
    for p in problems:
        print("Problem ID:", p["problem_id"])
        print("Title:", p["problem_title"])
        print("Top-level Date:", p["top_row_date"])
        print("Difficulty:", p["difficulty"])
        print("Submissions:")
        for sub in p["submissions"]:
            print("  -", sub)
        print("----")

if __name__ == "__main__":
    # Example usage:
    # process_leetcode_html_files(pattern_mode=None)  # to get all .html/.txt
    # process_leetcode_html_files(pattern_mode="number")    # files starting with a digit

    # process_leetcode_html_files(pattern_mode="progress")  # files starting with 'Progress'

    # process_leetcode_html_files()
    with open("scratch/Progress - LeetCode-12.html", "r", encoding="utf-8") as f:
        raw_html = f.read()

    parsed_problems = parse_leetcode_progress(raw_html)
    
    # 3) If you like, call the demo function to print out details
    demo_parsing(raw_html)

    # Or just inspect parsed_problems directly
    # for problem in parsed_problems:
    #     print(f"Problem: {problem['problem_id']} - {problem['problem_title']}")
    #     print(f"  Top-level date: {problem['top_row_date']}")
    #     print(f"  Submissions ({len(problem['submissions'])}):")
    #     for sub in problem['submissions']:
    #         print("    -", sub)
    #     print("------")