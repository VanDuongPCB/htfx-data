import os
import glob
from colorama import init, Fore, Style # type: ignore
import shutil
import json

def load_ignores():
    items = []

    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "jsonls", "categories.txt")
    if not os.path.exists(file_path):
        return items
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            items.append(line.lower().strip())
    return items


def get_meta_ignores():
    ignores = [
        "Video Games"
    ]
    return ignores
    pass

def get_meta_files(file_extension):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    meta_dir = os.path.join(base_dir,"meta")
    if not os.path.exists(meta_dir):
        return None
    
    meta_files = glob.glob(os.path.join(meta_dir, f"*{file_extension}"))
    return meta_files
    pass

def to_sqlite(output_file_path, buffers):
    import sqlite3

    if not os.path.exists(output_file_path):
        conn = sqlite3.connect(output_file_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                main_category TEXT NOT NULL,
                features TEXT NOT NULL,
                description TEXT NOT NULL,
                price TEXT NOT NULL,
                rating TEXT NOT NULL,
                image TEXT NOT NULL
            )
            """)
        conn.commit()
        conn.close()
        
    conn = sqlite3.connect(output_file_path)
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO products "\
        "(title, main_category, features, description, price, rating, image) "\
        "VALUES (:title, :main_category, :features, :description, :price, :rating, :image)", 
        buffers)
    conn.commit()
    conn.close()
    pass

def to_jsonl(output_file_path, buffers):
    pass

def to_csv(output_file_path, buffers):
    pass




def main():
    print("*** AMAZON EXTRACT DATA ***")
    print("1. To SQLITE")
    print("2. To JSONL")
    print("3. To CSV")
    choice = input("Select the options you want to extract: ")

    # Setup maximum line each file
    target_file = None
    if "1" in choice:
        target_file = "Amazon Products.db"

    elif "2" in choice:
        target_file = "Amazon Products.jsonl"

    elif "3" in choice:
        target_file = "Amazon Products.csv"

    else:
        return

    # Enumerate all CSV files in the Csv directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "filtereds")
    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} does not exist.")
        return
    
    extract_dir = os.path.join(base_dir, "extracts")
    os.makedirs(extract_dir, exist_ok=True)

    output_file_path = os.path.join(extract_dir, target_file)
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    
    # Maximum number of items to process from each file
    limit_max_line_default = 10000
    limit_max_line = limit_max_line_default
    limit_min_line_default = 200
    limit_min_line = limit_min_line_default
    input_text = input(f"Enter limit of items to process from each file (default {limit_max_line_default}): ")
    if input_text is not None and len(input_text.strip()) > 0:
        try:
            ivalue = int(input_text)
            if ivalue > 0:
                limit_max_line = ivalue
            pass
        except Exception as e:
            pass

    
    jsonl_files = glob.glob(os.path.join(input_dir, "*.jsonl"))
    for json_file in jsonl_files:
        buffers = []
        print(f"[ {Fore.LIGHTCYAN_EX}>>{Style.RESET_ALL} ] {json_file}", end="\r")
        if "/meta_" not in json_file and "\\meta_" not in json_file:
            print(f"[ {Fore.LIGHTYELLOW_EX}IG{Style.RESET_ALL} ] {json_file}")
            continue

        input_file = open(json_file, 'r', encoding='utf-8')
        for line in input_file:
            try:
                jsondata = json.loads(line)
                buffers.append(jsondata)
                if len(buffers) >= limit_max_line:
                    break
            except Exception as e:
                pass
        
        if len(buffers) < limit_min_line:
            print(f"[ {Fore.LIGHTYELLOW_EX}IG{Style.RESET_ALL} ] {json_file}")
        else:
            if target_file.endswith(".db"):
                to_sqlite(output_file_path, buffers)
            elif target_file.endswith(".jsonl"):
                to_jsonl(output_file_path, buffers)
            elif target_file.endswith(".csv"):
                to_csv(output_file_path, buffers)
            print(f"[ {Fore.LIGHTGREEN_EX}OK{Style.RESET_ALL} ] {json_file}")
        pass

    print(f"{Fore.LIGHTGREEN_EX}Extract to {output_file_path} succeeded!{Style.RESET_ALL}")
    pass


if __name__ == "__main__":
    main()
    pass