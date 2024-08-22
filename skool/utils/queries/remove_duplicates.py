import csv
from collections import OrderedDict


def remove_duplicates(input_file, output_file):
    unique_rows = OrderedDict()

    with open(input_file, "r", newline="") as csvfile:
        reader = csv.reader(csvfile)

        header = next(reader, None)

        for row in reader:
            row_tuple = tuple(row)

            if row_tuple not in unique_rows:
                unique_rows[row_tuple] = None

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        if header:
            writer.writerow(header)

        for row in unique_rows.keys():
            writer.writerow(row)

    print(f"Arquivo CSV sem duplicatas salvo como '{output_file}'")


input_file = "entrada.csv"
output_file = "saida_sem_duplicatas.csv"
remove_duplicates(input_file, output_file)
