import pandas as pd
import argparse
from urllib.parse import urlparse
import requests

condition_mapping = {
    "Mint": "Mint",
    "NearMint": "NM",
    "Excellent": "LP",
    "Good": "LP",
    "LightPlayed": "MP",
    "Played": "HP",
    "Poor": "DM"
}

foil_mapping = {
    "Normal": "",
    "Foil": "1"
}

def extract_deck_info(url):
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split('/')
    # path segments example: ['', 'decks', '111111', '1111111-standard']
    if len(path_segments) >= 4:
        user_id = path_segments[2]
        deck_id = path_segments[3].split('-')[0]
        return user_id, deck_id
    return None, None

def fetch_deck_data(user_id, deck_id):
    api_url = f"https://deckstats.net/api.php?action=get_deck&id_type=saved&owner_id={user_id}&id={deck_id}&response_type=json"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch deck data from {api_url}, error: {e}")
        return None

def read_csv_file(filepath):
    return pd.read_csv(filepath, skiprows=1, quotechar='"', escapechar="\\")

def aggregate_cards(collection_data):
    # group by all relevant columns except 'Quantity' and sum the quantities
    aggregation_columns = ['Card Name', 'Set Code', 'Card Number', 'Condition', 'Printing', 'Language']
    collection_data['Quantity'] = collection_data.groupby(aggregation_columns)['Quantity'].transform('sum')
    # drop duplicates after summing quantities
    return collection_data.drop_duplicates(subset=aggregation_columns)

def xor_deck(collection_data, deck_data):
    basic_lands = {"Forest", "Mountain", "Plains", "Island", "Swamp", "Wastes"}
    for section in deck_data.get('sections', []):
        for card in section.get('cards', []):
            card_name = card['name']
            if card_name in basic_lands:
                continue
            card_amount = card['amount']
            collector_number = card.get('collector_number', None)
            is_foil = "Foil" if card.get('isFoil') else "Normal"
            conditions = (collection_data['Card Name'] == card_name) & (collection_data['Printing'] == is_foil)

            # add collector number to the conditions if it's available
            if collector_number:
                # api returns collector number as a string
                conditions &= (collection_data['Card Number'] == int(collector_number))

            print(f"Looking for {card_amount} of {card_name} ({is_foil})" if collector_number is None else f"Looking for {card_amount} of {card_name} ({is_foil}) with collector number {collector_number}")
            matches = collection_data.loc[conditions]
            print(f"Found {len(matches)} matches for {card_name} ({is_foil})")
            
            for idx in matches.index:
                if card_amount > 0:
                    remove_amount = min(matches.at[idx, 'Quantity'], card_amount)
                    collection_data.at[idx, 'Quantity'] -= remove_amount
                    card_amount -= remove_amount

    # filter out cards where the quantity has been reduced to zero or less
    return collection_data[collection_data['Quantity'] > 0]



def remap_csv(input_csv_file_path="./input.csv", output_file_path="./output.csv", deck_url=None):
    collection_data = read_csv_file(input_csv_file_path)
    collection_data = aggregate_cards(collection_data)
    if deck_url:
        user_id, deck_id = extract_deck_info(deck_url)
        deck_json = fetch_deck_data(user_id, deck_id)
        collection_data = xor_deck(collection_data, deck_json)
    remapped_data = pd.DataFrame({
        "amount": collection_data['Quantity'],
        "card_name": collection_data['Card Name'],
        "set_name": collection_data['Set Code'],
        "condition": collection_data['Condition'].map(condition_mapping),
        "language": collection_data['Language'],
        "is_foil": collection_data['Printing'].map(foil_mapping),
        "collector_number": collection_data['Card Number'],
        "added": collection_data['Date Bought']
    })
    remapped_data.to_csv(output_file_path, index=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="Path to the input CSV file. Default: `./input.csv`", default="./input.csv")

    parser.add_argument("--deckUrl", help="URL to deckstats deck. Default: None")
    args = parser.parse_args()
    input_csv_file_path = args.path
    deck_url = args.deckUrl

    remap_csv(input_csv_file_path, "./output.csv", deck_url)

if __name__ == "__main__":
    main()