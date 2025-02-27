import csv

def combine_problems(neetcode_file, leetcode_file, output_file):
    combined_dict = {}

    # 1. Read leetcode_problems.csv into combined_dict
    with open(leetcode_file, 'r', encoding='utf-8') as lf:
        reader = csv.DictReader(lf)
        for row in reader:
            title = row['problem_title'].strip()
            combined_dict[title] = {
                'problem_title': title,
                'Topic': '',
                'problem_id': row['problem_id'].strip(),
                'difficulty': row['difficulty'].strip(),
                'last_result': row['last_result'].strip(),
                'url': row['url'].strip()
            }

    # 2. Read neetcode150.csv, fill in Topic or add new entries
    with open(neetcode_file, 'r', encoding='utf-8') as nf:
        reader = csv.DictReader(nf)
        for row in reader:
            problem_title = row['Problem'].strip()
            topic = row['Topic'].strip() if 'Topic' in row else ''

            if problem_title in combined_dict:
                # If it's already in LeetCode data, just add the topic
                combined_dict[problem_title]['Topic'] = topic
            else:
                # Otherwise, add a new entry with blanks for everything else
                combined_dict[problem_title] = {
                    'problem_title': problem_title,
                    'Topic': topic,
                    'problem_id': '',
                    'difficulty': '',
                    'last_result': '',
                    'url': ''
                }

    # 3. Write all rows in combined_dict to a new CSV
    fieldnames = ["problem_title", "Topic", "problem_id", "difficulty", "last_result", "url"]
    with open(output_file, 'w', newline='', encoding='utf-8') as out:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for data in combined_dict.values():
            writer.writerow(data)

    # 4. Print missing (uncompleted) problems (those with no problem_id)
    missing = [title for title, info in combined_dict.items() if not info['problem_id']]
    print("Missing (uncompleted) problems:")
    for prob in missing:
        print(prob)
    print(f"Total missing: {len(missing)}")


if __name__ == "__main__":
    combine_problems(
        neetcode_file='neetcode150.csv',
        leetcode_file='leetcode_problems.csv',
        output_file='combined.csv'
    )
