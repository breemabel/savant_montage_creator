from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time
import os
from datetime import date, datetime, timedelta
from moviepy.editor import concatenate_videoclips, VideoFileClip
import random


def get_player_ids(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    player_ids = []

    # Find the table with id "search_results"
    table = soup.find('table', {'id': 'search_results'})
    if table:
        # Find all rows in the table
        rows = table.find_all('tr')
        for row in rows:
            # Check if the row has a data-player-id attribute
            player_id = row.get('data-player-id')
            if player_id:
                player_ids.append(player_id)

    return player_ids

def process_players(player_ids, player_url):
    video_urls = []

    # Configure Chrome WebDriver options
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    service = Service('D:\Downloads\chromedriver.exe')  # Set the path to chromedriver executable

    # Start the Chrome WebDriver
    driver = webdriver.Chrome(service=service, options=options)
    
    # Load the webpage
    driver.get(player_url)
    time.sleep(2)

    for player_id in player_ids:
        player_row = driver.find_element(By.ID, f"player_name_{player_id}_")

        # Simulate click on the player row using JavaScript
        driver.execute_script("arguments[0].click();", player_row)
        time.sleep(2)

        # Extract the HTML content after the page has fully loaded
        html = driver.page_source

        # Parse the HTML content
        soup = BeautifulSoup(html, 'html.parser')

        # Find the details row
        details_row = soup.find('tr', {'id': f'details_name_{player_id}_'})
        if details_row:
            print(f"Details row found for player ID: {player_id}")

            # Find the nested table within the details row
            nested_table = details_row.find('table', {'id': f'ajaxTable_{player_id}'})
            if nested_table:
                print(f"Nested table found for player ID: {player_id}")

                # Find the rows within the nested table
                nested_rows = nested_table.find_all('tr')
                for nested_row in nested_rows[1:]:
                    # Extract video link
                    video_link = nested_row.find('a').get('href')
                    video_url = f'https://baseballsavant.mlb.com{video_link}'
                    print(f"Video URL for player ID {player_id}: {video_url}")
                    video_urls.append(video_url)

            else:
                print(f"No nested table found for the details row of player ID: {player_id}")
        else:
            print(f"No details row found for player ID: {player_id}")

    # Close the WebDriver
    driver.quit()

    return video_urls

def get_video_links(video_urls):
    video_links = []

    for video_url in video_urls:
        response = requests.get(video_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        video_tag = soup.find('video', id='sporty')
        if video_tag:
            source_tag = video_tag.find('source')
            if source_tag:
                video_link = source_tag['src']
                video_links.append(video_link)
    
    return video_links

def download_videos(video_links):
    # Create a folder with yesterday's date
    yesterday = date.today() - timedelta(days=1)
    folder_name = yesterday.strftime("%Y-%m-%d")
    output_folder = os.path.join("D:", "Home Runs", folder_name)
    os.makedirs(output_folder, exist_ok=True)

    # Download the videos
    video_paths = []
    for i, video_link in enumerate(video_links):
        output_path = os.path.join(output_folder, f"video{i}.mp4")
        download_video(video_link, output_path)
        video_paths.append(output_path)
        print(f"Video {i+1}/{len(video_links)} downloaded successfully!")

    return video_paths


def download_video(video_url, output_path):
    response = requests.get(video_url)

    with open(output_path, 'wb') as file:
        file.write(response.content)


def combine_videos(video_paths, output_file):
    clips = [VideoFileClip(path) for path in video_paths]
    concatenated_clip = concatenate_videoclips(clips)
    concatenated_clip.write_videofile(output_file, codec='libx264')


def main():
    now = datetime.now()
    yesterday = date.today() - timedelta(days=1)
    two_days_ago = date.today() - timedelta(days=2)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    two_days_ago_str = two_days_ago.strftime("%Y-%m-%d")

    if now.hour >= 9:
        # Use yesterday's date
        url = f'https://baseballsavant.mlb.com/statcast_search?hfPTM=&hfPT=&hfAB=home%5C.%5C.run%7C&hfGT=R%7CPO%7CA%7C&hfPR=&hfZ=&hfStadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea=2023%7C&hfSit=&player_type=batter&hfOuts=&hfOpponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={yesterday_str}&game_date_lt=&hfMo=&hfTeam=&home_road=&hfRO=&position=&hfInfield=&hfOutfield=&hfInn=&hfBBT=&hfFlag=&metric_1=&group_by=name&min_pitches=0&min_results=0&min_pas=0&sort_col=pitches&player_event_sort=api_p_release_speed&sort_order=desc#results'
    else:
        # Use two days ago's date
        url = f'https://baseballsavant.mlb.com/statcast_search?hfPTM=&hfPT=&hfAB=home%5C.%5C.run%7C&hfGT=R%7CPO%7CA%7C&hfPR=&hfZ=&hfStadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea=2023%7C&hfSit=&player_type=batter&hfOuts=&hfOpponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={two_days_ago_str}&game_date_lt=&hfMo=&hfTeam=&home_road=&hfRO=&position=&hfInfield=&hfOutfield=&hfInn=&hfBBT=&hfFlag=&metric_1=&group_by=name&min_pitches=0&min_results=0&min_pas=0&sort_col=pitches&player_event_sort=api_p_release_speed&sort_order=desc#results'
    player_ids = get_player_ids(url)
    video_urls = process_players(player_ids, url)
    video_links = get_video_links(video_urls)
    random.shuffle(video_links)
    
    video_paths = download_videos(video_links)
    
    # Create a folder with yesterday's date
    yesterday = date.today() - timedelta(days=1)
    folder_name = yesterday.strftime("%Y-%m-%d")
    output_folder = os.path.join("D:", "Home Runs", folder_name)
    os.makedirs(output_folder, exist_ok=True)
    
    # Combine the videos
    output_file = os.path.join(output_folder, "combined_video.mp4")
    combine_videos(video_paths, output_file)
    
    print("Videos downloaded and combined successfully!")

if __name__ == '__main__':
    main()

