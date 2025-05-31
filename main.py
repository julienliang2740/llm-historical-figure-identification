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
know_by_bio_test = False

def process_row(row: Dict[str, str]) -> Dict[str, str]:
    # """
    # Stub function that takes in one CSV row (as a dict) and returns an updated dict.
    # Modify this function to “do stuff” on each line.

    # Example modifications shown below; feel free to replace with your own logic.
    # """
    # # EXAMPLE: If “know_by_name” is empty, fill in a default:
    # if not row["know_by_name"].strip():
    #     row["know_by_name"] = "UNKNOWN"

    # # EXAMPLE: Append “ (reviewed)” to the summary column
    # row["know_by_bio_summary"] = row["know_by_bio_summary"] + " (reviewed)"

    # # EXAMPLE: If the name column contains lowercase, convert to title-case
    # row["name"] = row["name"].strip().title()

    # # EXAMPLE: If a link is missing, set a placeholder URL
    # if not row["know_by_bio_link"].startswith("http"):
    #     row["know_by_bio_link"] = "https://example.com/no-link"

    # # …any other “per-row” logic goes here…

    # return row



    # first check if there's even a name, if now just return and call it a day
    if not row["name"].strip():
        return row

    # RECOGNITION TEST ONE know_by_name_test
    # headers affected: know_by_name,know_by_name_description
    if know_by_name_test:
        if not row["know_by_name"].strip():
            user_prompt = row["name"]
            result_dict = run_api(know_by_name_prompt, user_prompt, "know_by_name")
            row["know_by_name"] = result_dict["recognize"]
            row["know_by_name_description"] = result_dict["description"]

    # RECOGNITION TEST TWO know_by_bio_test
    #  headers affected: know_by_bio, know_by_bio_link, know_by_bio_summary, know_by_bio_summary_anonymized, know_by_bio_reasoning
    if know_by_bio_test:
        pass

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
    # Example usage:
    input_csv = "people_trunc.csv"
    output_csv = "people_output_trunc.csv"
    print(f"Processing '{input_csv}' → '{output_csv}' …")
    process_csv_lines(input_csv, output_csv)
    print("Finished.")
