import requests, os, re, sys
from bs4 import BeautifulSoup

# Get URL from command line argument or user input
if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    url = input("Enter Episode URL or Show URL: ")

# Send a GET request to the URL
res = requests.get(url)

# Create a BeautifulSoup object to parse the HTML content
soup = BeautifulSoup(res.content, "html.parser")

# Extract show name
title_details = soup.find("a", {"id": "TitleDetails"})
if title_details:
    show_name = title_details.text.strip()
else:
    show_name = soup.find("div", {"class": "text-container"}).find("h1").text.strip()

# Replace "Oshi No Ko" with "Oshi no Ko"
show_name = show_name.replace("Oshi No Ko", "Oshi no Ko")

def get_episode_info(soup, show_name):
    # Extract episode number and name
    stream_title_description = soup.find("div", {"id": "StreamTitleDescription"})
    episode_number = (
        stream_title_description.find_all("h2")[0].text.split("|")[0].strip()
    )
    episode_name = stream_title_description.find_all("h2")[1].text.strip()

    # Remove "Season X" from episode info
    episode_number = episode_number.replace("Season 1 ", "")
    episode_number = episode_number.replace("Season 2 ", "")
    episode_number = episode_number.replace("Season 3 ", "")

    # Remove everything before ": " in episode name
    if ": " in episode_name:
        episode_name = episode_name.split(": ")[1]

    # Replace "/" with "⧸"
    episode_name = episode_name.replace("/", "⧸")

    # Find the image with alt attribute that matches the episode number
    img_tag = soup.find("img", alt=re.compile(episode_number))

    # Extract image URL
    img_url = "https:" + img_tag["src"]

    # Print formatted output and save the image
    filename = f"{show_name} {episode_number} - {episode_name}.jpeg"
    path = os.path.join(os.path.expanduser("~"), "Downloads", filename)
    img_data = requests.get(img_url).content
    with open(path, "wb") as handler:
        handler.write(img_data)
        print(f"Image saved as {filename} in {os.path.dirname(path)}")

# Check if it's an episode page
stream_title_description = soup.find("div", {"id": "StreamTitleDescription"})
if stream_title_description:
    get_episode_info(soup, show_name)
else:
    processed_links = set()  # to store already processed links

    url_pattern = f'stream/{url.split(".com/tv/")[1].split("/")[0]}/.*'
    stream_links = soup.find_all("a", href=re.compile(url_pattern))

    for link in stream_links:
        href = link["href"]
        if href not in processed_links:
            processed_links.add(href)
            
            # Print link to show stream
            # print(href)

            # Find link to show stream
            episode_url = "https://www.hidive.com" + href
            episode_res = requests.get(episode_url)
            episode_soup = BeautifulSoup(episode_res.content, "html.parser")

            # Extract episode details and save image
            get_episode_info(episode_soup, show_name)