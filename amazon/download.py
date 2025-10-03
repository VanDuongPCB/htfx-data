import os
from colorama import init, Fore, Style # type: ignore
from huggingface_hub import list_repo_files, hf_hub_download
import shutil

def main():
    print("*** AMAZON HUGGINGFACE DATA DOWNLOADER ***")

    repo_id = "McAuley-Lab/Amazon-Reviews-2023"
    files = list_repo_files(repo_id, repo_type="dataset")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    jsonl_dir = os.path.join(base_dir,"jsonls")
    os.makedirs(jsonl_dir, exist_ok=True)
    
    for file in files:
        if not file.lower().endswith(".jsonl"):
            continue
        
        if not file.startswith("raw/meta_categories/meta_"):
            continue

        filename = file
        category = file.replace("raw/meta_categories/","")
        output_file = os.path.join(jsonl_dir, category)
        
        if os.path.exists(output_file):
            print(f"[ {Fore.GREEN}DOWNLOADED{Style.RESET_ALL} ] {category}")
            continue

        print(f"[ {Fore.YELLOW}DOWNLOADING{Style.RESET_ALL} ] {category}",end="\r")
        try:
            local_path = hf_hub_download(repo_id, filename, repo_type="dataset", cache_dir=jsonl_dir)
            shutil.move(local_path, output_file)
            print(f"[ {Fore.GREEN}DOWNLOADED{Style.RESET_ALL} ] {category}")
            pass
        except Exception as e:
            print(f"[ {Fore.RED}ERROR      {Style.RESET_ALL} ] {category}")
            pass


    # Remove cache folders
    need_remove_dirs = [
        os.path.join(jsonl_dir, ".locks"),
        os.path.join(jsonl_dir, "datasets--McAuley-Lab--Amazon-Reviews-2023")
    ]

    for dir in need_remove_dirs:
        if os.path.exists(dir):
            try:
                shutil.rmtree(dir)
            except Exception as e:
                print(e)
                pass

            
if __name__ == "__main__":
    init(autoreset=True)
    main()
    pass