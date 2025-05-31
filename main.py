from model import *
from crawl import *

import csv
from typing import Dict

"""
csv headers legend:
name: name -> Name of the person
know_by_name: yes/no -> RECOGNITION TEST ONE (whether the llm directly recognizes the name)
know_by_bio: name -> RECOGNITION TEST TWO (whether the llm guesses the right person based on a summary)
know_by_name_description: text -> Brief description of the person that the llm gives for RECOGNITION TEST ONE (if it recognizes the person)
know_by_bio_link: link -> Link to crawl to get summary for RECOGNITION TEST TWO
know_by_bio_summary: text -> Summary of person given to llm for RECOGNITION TEST TWO
know_by_bio_summary_anonymized: text -> Anonymized summary of person given to llm for RECOGNITION TEST TWO
know_by_bio_reasoning: text -> Brief reasoning the llm gives for why they think its that person
"""

know_by_name_test = True
know_by_bio_test = True

# debug function for printing out a line
def print_csv_line_from_file(filename, line_number, has_headers=False):
    with open(filename, 'r', newline='') as file:
        reader = csv.reader(file)
        rows = list(reader)

        if line_number < 1 or line_number > len(rows):
            print(f"Line number {line_number} is out of range. File has {len(rows)} lines.")
            return

        if has_headers:
            headers = rows[0]
            data_row = rows[line_number]
            print(f"\nLine {line_number}:")
            for header, value in zip(headers, data_row):
                print(f"{header}: {value}")
        else:
            data_row = rows[line_number - 1]
            print(f"\nLine {line_number}:")
            for index, value in enumerate(data_row):
                print(f"Column {index}: {value}")

def process_row(row: Dict[str, str]) -> Dict[str, str]:
    # first check if there's even a name, if now just return and call it a day
    if row["name"].strip() == "":
        return row

    # RECOGNITION TEST ONE know_by_name_test
    # headers affected: know_by_name,know_by_name_description
    if know_by_name_test:
        if row["know_by_name"].strip() == "":
            print(f"{row["name"]}: conducting know_by_name_test")
            user_prompt = row["name"]
            result_dict = run_api(know_by_name_prompt, user_prompt, "know_by_name")
            row["know_by_name"] = result_dict["recognize"]
            row["know_by_name_description"] = result_dict["description"]
        else:
            print("RECOGNITION TEST ONE FILLED IN")

    # RECOGNITION TEST TWO know_by_bio_test
    #  headers affected: know_by_bio, know_by_bio_link, know_by_bio_summary, know_by_bio_summary_anonymized, know_by_bio_reasoning
    if know_by_bio_test:
        if row["know_by_bio"].strip() == "":
            print("MONKE BRUGA PROCEEDING")
            if row["know_by_bio_summary_anonymized"].strip() == "":
                if row["know_by_bio_summary"].strip() == "":
                    if row["know_by_bio_link"].strip() == "":
                        print("NO LINK TO GET")
                        print(row)
                        return row
                    crawled_text = crawl_link(row["know_by_bio_link"].strip())
                    row["know_by_bio_summary"] = crawled_text.replace('\n',' ')
                row["know_by_bio_summary_anonymized"] = run_api(anonymize_biography_prompt, row["know_by_bio_summary"], "anonymize_biography")

            user_prompt = row["know_by_bio_summary_anonymized"]
            result_dict = run_api(know_by_bio_prompt, user_prompt, "know_by_bio")
            row["know_by_bio"] = result_dict["name_guess"]
            row["know_by_bio_reasoning"] = result_dict["reasoning"].replace('\n',' ')
        else:
            print("RECOGNITION TEST TWO FILLED IN")

    print(row)
    return row

# VERY IMPORTANT NOTE: THIS FUNCTION SKIPS OVER ANY LINE THAT SEEMS TO BE COMPLETED (HAS STUFF IN IT CORRESPONDING TO THE TYPE OF TEST WE'RE RUNNING)
# Ex. if know_by_name_test and know_by_bio_test are both set to true, and in one line the know_by_bio_test info is filled in, it won't do that part
# ^(it'll just write what already exists over to the new file)
def process_csv_lines(input_filename: str, output_filename: str) -> None:
    """
    Reads a CSV with headers:
       name,
       know_by_name,
       know_by_bio,
       know_by_name_description,
       know_by_bio_link,
       know_by_bio_summary,
       know_by_bio_summary_anonymized,
       know_by_bio_reasoning

    For each row, calls process_row(row) to get an updated row dict,
    then writes the updated dict into output_filename (same headers).
    """
    with open(input_filename, mode="r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise ValueError("Input CSV must have headers.")

        with open(output_filename, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                # Call the stub function to “process” this row
                updated_row = process_row(row)

                # Write the updated row to the new CSV
                writer.writerow(updated_row)

    print(f"Done processing. Output saved to '{output_filename}'.")


if __name__ == "__main__":
    if True:
        # Example usage:
        input_csv = "./data/batch1.csv"
        output_csv = "./data/batch1_output3.csv"
        print(f"Processing '{input_csv}' → '{output_csv}' …")
        process_csv_lines(input_csv, output_csv)
        print("Finished.")

    if True:
        # Debug usage:
        debug_csv = "./data/people_output_trunc.csv"
        line_number = 2
        print(f"Printing: {debug_csv} - line {line_number}")
        print_csv_line_from_file(debug_csv, line_number)
        line_number = 3
        print(f"Printing: {debug_csv} - line {line_number}")
        print_csv_line_from_file(debug_csv, line_number)

