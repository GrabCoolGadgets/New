from pymongo import MongoClient
import requests
import base64

# MongoDB connection
client = MongoClient("mongodb+srv://Ipopcorninline:Ipopcorninline@cluster0.8uues.mongodb.net/")
db = client["iPopcornApp"]
collection = db["iPopcornData"]

# GitHub config
GITHUB_TOKEN = "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"
REPO = "GrabCoolGadgets/ip"
FILE_PATH = "data/posts.txt"

def format_posts(posts):
    result = ""
    for post in posts:
        if "text" in post:
            lines = [line.strip() for line in post["text"].split('\n') if line.strip()]
            compressed = ""
            for i, line in enumerate(lines):
                if line.endswith("{"):
                    compressed += lines[i].replace("{", "") + "{"
                elif line == "}":
                    compressed += "}"
                else:
                    compressed += line + " "
            result += compressed.strip() + "\n"
    return result.strip()

def update_github_file(new_content):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    
    # Get current file SHA
    res = requests.get(url, headers=headers)
    sha = res.json().get('sha', None)

    encoded_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": "Updated from MongoDB",
        "content": encoded_content,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    put_res = requests.put(url, headers=headers, json=payload)
    print(f"GitHub Update Status: {put_res.status_code}")
    print(put_res.text)

if __name__ == "__main__":
    posts = list(collection.find())
    formatted = format_posts(posts)
    update_github_file(formatted)
