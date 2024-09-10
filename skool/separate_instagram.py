import csv
import os

# Função para determinar o diretório do script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Caminhos dos arquivos
input_file = os.path.join(script_dir, "timyoon_members_followers2.csv")
output_with_instagram = os.path.join(script_dir, "timyoon_members_followers_with_instagram.csv")
output_without_instagram = os.path.join(script_dir, "timyoon_members_followers_without_instagram.csv")

# Lê o arquivo CSV de entrada
with open(input_file, "r", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)

    # Prepara os escritores para os arquivos de saída
    with open(output_with_instagram, "w", newline="", encoding="utf-8") as file_with, open(
        output_without_instagram, "w", newline="", encoding="utf-8"
    ) as file_without:
        fieldnames = reader.fieldnames
        writer_with = csv.DictWriter(file_with, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer_without = csv.DictWriter(file_without, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

        # Escreve os cabeçalhos em ambos os arquivos
        writer_with.writeheader()
        writer_without.writeheader()

        # Processa cada linha do arquivo de entrada
        for row in reader:
            if row["instagram"]:
                writer_with.writerow(row)
            else:
                writer_without.writerow(row)

print(f"Processamento concluído. Os resultados foram salvos em '{output_with_instagram}' e '{output_without_instagram}'.")
