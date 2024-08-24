import os
import re
import csv


def adjust_csv(input_file, output_file):
    url_pattern = r"(https?://[^/]+/[^/]+/[^/]+)(?=https?:|$)"

    with open(input_file, "r", newline="", encoding="utf-8") as infile, open(output_file, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for row in reader:
            content = row[0] if row else ""

            urls = re.findall(url_pattern, content)

            for url in urls:
                writer.writerow([url])


current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir_abspath = os.path.abspath(current_dir)
input_file = os.path.join(current_dir_abspath, "unique_urls.csv")
output_file = os.path.join(current_dir_abspath, "urls_formatted.csv")
adjust_csv(input_file, output_file)
