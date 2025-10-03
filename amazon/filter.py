import os
from colorama import init, Fore, Style # type: ignore
import shutil
import glob
import json

meta_data_buffers = {}
review_data_buffers = {}

def get_main_category(jsondata):
    text = jsondata.get("main_category", None)
    if text is None:
        return None
    return text
    pass

def get_title(jsondata):
    text = jsondata.get("title", None)
    if text is None:
        return None
    return text
    pass

def get_item_id(jsondata):
    text = jsondata.get("parent_asin", None)
    if text is None:
        return None
    return text
    pass

def get_categories(jsondata):
    if jsondata.get("categories", None) is None:
        return None
    
    categories = jsondata.get("categories", [])
    if categories is None or len(categories) <1:
        return None
    
    return categories
    pass

def get_features(jsondata):
    features = jsondata.get("features", [])
    if features is None or len(features) <1:
        return None
    
    features = " ".join(features)
    if features.lower().strip() in ["none","null","nil",""]:
        return None 

    return features
    pass

def get_description(jsondata):
    description = jsondata.get("description", [])
    if description is None or len(description) <1:
        return None
    
    description = " ".join(description)
    if description.lower().strip() in ["none","null","nil",""]:
        return None 
    
    return description
    pass

def get_image(jsondata):
    images = jsondata.get("images",None)
    if images is None or len(images) < 1 or "large" not in images[0]:
        return None

    image = images[0]["large"]
    return image
    pass

def get_price(jsondata):
    price = str(jsondata.get("price","20"))
    if price is None or price.strip().lower() in ["none","null","nill",""]:
        price = "20"
    return price
    pass

def get_rating(jsondata):
    rating = str(jsondata.get("average_rating","4"))
    if rating is None or rating.strip().lower() in ["none","null","nill",""]:
        rating = "4"
    return rating
    pass

def write_to_csv(file_path, data, key, headers):
    print(f"Write file {file_path}")

    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(headers + ",\n")
    
    with open(file_path, "a", encoding="utf-8") as f:
        for item in data[key]:
            f.write(",".join(item) + ",\n")
    data[key] = []
    pass

def filter_meta():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    jsonl_dir = os.path.join(base_dir,"jsonls")
    if not os.path.exists(jsonl_dir):
        return
    filtered_dir = os.path.join(base_dir,"filtereds")
    if os.path.exists(filtered_dir):
        shutil.rmtree(filtered_dir)
    os.makedirs(filtered_dir, exist_ok= True)

    buffers = {}
    jsonl_files = glob.glob(os.path.join(jsonl_dir, "*.jsonl"))
    for json_file in jsonl_files:
        print(f"[ ... ] {json_file}", end="\r")
        if "/meta_" not in json_file and "\\meta_" not in json_file:
            print(f"[ {Fore.YELLOW}IGN{Style.RESET_ALL} ] {json_file}")
            continue

        input_file = open(json_file, 'r', encoding='utf-8')
        for line in input_file:
            try:
                jsondata = json.loads(line)

                main_category = get_main_category(jsondata)
                if main_category is None:
                    continue
                main_category = main_category.strip().replace("\"","")
                main_category = main_category.title()

                item_id = get_item_id(jsondata)
                if item_id is None:
                    continue
                item_id = item_id.strip().replace("\"","")

                title = get_title(jsondata)
                if title is None:
                    continue
                title = title.strip().replace("\"","")

                features = get_features(jsondata)
                if features is None:
                    continue
                features = features.strip().replace("\"","")

                description = get_description(jsondata)
                if description is None:
                    continue
                description = description.strip().replace("\"","")

                price = get_price(jsondata)
                rating = get_rating(jsondata)
                image = get_image(jsondata)
                if image is None:
                    continue
                image = image.strip().replace("\"","")



                item = {
                    "main_category": main_category,
                    "item_id" : item_id,
                    "title" : title,
                    "features" : features,
                    "description" : description,
                    "price": price,
                    "rating": rating,
                    "image": image
                }

                if main_category not in buffers:
                    buffers[main_category] = []
                
                buffers[main_category].append(item)
                if len(buffers[main_category]) >= 100000:
                    output_file_path =  os.path.join(filtered_dir, f"meta_{main_category}.jsonl")
                    mode = "a" if os.path.exists(output_file_path) else "w"
                    with open(output_file_path, mode, encoding="utf-8") as f:
                        for item in buffers[main_category]:
                            f.write(json.dumps(item, ensure_ascii=False) + "\n")
                    buffers[main_category] = []
                    pass
                pass
            except Exception as e:
                pass
        print(f"[ {Fore.GREEN}OK {Style.RESET_ALL} ] {json_file}")


    for main_category, items in buffers.items():
        if len(items) > 0:
            output_file_path =  os.path.join(filtered_dir, f"meta_{main_category}.jsonl")
            mode = "a" if os.path.exists(output_file_path) else "w"
            with open(output_file_path, mode, encoding="utf-8") as f:
                for item in items:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
            pass
    pass

def filter_review():
    
    pass

def main():
    print("*** AMAZON FILTER DATA ***")
    filter_meta()

if __name__ == "__main__":
    init(autoreset=True)
    main()
    pass