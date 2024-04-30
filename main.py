import pandas as pd
import argparse

condition_mapping = {
    "Mint": "M",
    "NearMint": "NM",
    "LightlyPlayed": "LP",
    "Played": "MP",
    "HeavilyPlayed": "HP",
    "Damaged": "DM"
}

foil_mapping = {
    "Normal": "",
    "Foil": "foil"
}

def xor_deck(data, deck_path):
   # WIP
   return data

def remap_csv(input_csv_file_path="./input.csv", output_file_path="./output.csv", deck_path=None):
    if deck_path:
        data = xor_deck(data, deck_path)
    data = pd.read_csv(input_csv_file_path, skiprows=1)
    remapped_data = pd.DataFrame({
        "Count": data['Quantity'],
        "Name": data['Card Name'],
        "Edition": data['Set Code'],
        "Condition": data['Condition'].map(condition_mapping),
        "Language": data['Language'],
        "Foil": data['Printing'].map(foil_mapping),
        "Collector Number": data['Card Number']
    })
    
    remapped_data.to_csv(output_file_path, index=False)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--path", help="Path to the input CSV file. Default: `./input.csv`", default="./input.csv")
  parser.add_argument("--dp", help="Path to the deck CSV file. Default: `./deck.csv`", default="./deck.csv")
  args = parser.parse_args()
  input_csv_file_path = args.path
  deck_path = args.dp

  remap_csv(input_csv_file_path, "./output.csv", deck_path)

if __name__ == "__main__":
  main()