"""
Main module for the application.
"""
import os
import re
import requests
import argparse
from pathlib import Path
from bs4 import BeautifulSoup, Tag

def download_webpage(url, output_path):
    """
    Download a webpage and save it to the specified path.
    
    Args:
        url (str): The URL of the webpage to download
        output_path (str): The path where the downloaded content will be saved
    
    Returns:
        bool: True if download was successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Download the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print(f"Downloading {url}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Save the content to a file
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Successfully downloaded to {output_path}")
        return True
    
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def extract_games_from_html(html_content, min_year=85, max_year=95):
    """
    Extract games from HTML content.
    
    Args:
        html_content (str): HTML content to parse
        min_year (int): Minimum year to include (default: 85)
        max_year (int): Maximum year to include (default: 95)
        
    Returns:
        list: List of dictionaries containing game information
    """
    try:
        soup = BeautifulSoup(html_content, 'lxml')
    except:
        # Fallback to html.parser if lxml is not available
        soup = BeautifulSoup(html_content, 'html.parser')
    
    games = []
    seen_titles = set()  # Set to track seen titles to avoid duplicates
    
    # Find all tables in the document
    tables = soup.find_all('table')
    
    for table in tables:
        # Get the region from the previous heading
        prev_heading = table.find_previous(['h2', 'h3'])
        if not prev_heading:
            continue
            
        region_text = prev_heading.get_text().strip().lower()
        
        # Only process North American games
        if 'north america' not in region_text:
            continue
            
        current_region = 'North America'
        print(f"Processing region: {current_region}")
        
        # Check if this is a game table by looking at the header row
        header_row = table.find('tr')
        if not header_row:
            continue
            
        header_cells = header_row.find_all(['th', 'td'])
        header_texts = [cell.get_text().strip().lower() for cell in header_cells]
        
        # Check if this looks like a game table (has title and publisher columns)
        if not ('title' in header_texts or 'game' in header_texts):
            continue
        
        # Process the table rows
        rows = table.find_all('tr')[1:]  # Skip header row
        
        for row in rows:
            try:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    title = cells[0].get_text().strip()
                    
                    # Skip unlicensed games
                    if "(Unlicensed)" in title:
                        continue
                        
                    publisher = cells[1].get_text().strip()
                    release_date = cells[2].get_text().strip()
                    
                    # Extract year from release date
                    year_match = re.search(r'19(\d{2})', release_date)
                    if year_match:
                        year = int(year_match.group(1))
                        if min_year <= year <= max_year:
                            # Check if we've already seen this title
                            # Create a unique key using title and year to handle same title in different years
                            unique_key = f"{title}_{year}_{current_region}"
                            if unique_key not in seen_titles:
                                seen_titles.add(unique_key)
                                games.append({
                                    'title': title,
                                    'publisher': publisher,
                                    'year': year,
                                    'release_date': release_date,
                                    'region': current_region
                                })
            except (IndexError, AttributeError, ValueError):
                # Skip rows that cause errors
                continue
    
    return games

def rename_rom_file(old_name, year, publisher, roms_dir):
    """
    Rename a ROM file to include year and publisher information.
    
    Args:
        old_name (str): Original filename
        year (int): Game release year
        publisher (str): Game publisher
        roms_dir (Path): Path to the ROMs directory
    """
    try:
        # Get the file extension
        ext = os.path.splitext(old_name)[1]
        
        # Get the base name without extension and (USA) or (usa)
        base_name = old_name.replace(ext, '').replace(' (USA)', '').replace(' (usa)', '').strip()
        
        # Create new filename
        new_name = f"{year} - {base_name} (USA) ({publisher}){ext}"
        
        # Full paths
        old_path = roms_dir / old_name
        new_path = roms_dir / new_name
        
        # Show proposed change and ask for confirmation
        print(f"\nProposed rename:")
        print(f"From: {old_name}")
        print(f"To:   {new_name}")
                
        # Rename the file
        old_path.rename(new_path)
        print(f"Renamed: {old_name} -> {new_name}")
        return True
            
    except Exception as e:
        print(f"Error renaming {old_name}: {e}")
        return False

def check_rom_exists(title, roms_dir, year=None, publisher=None):
    """
    Check if a ROM file exists for the given game title.
    
    Args:
        title (str): Game title to check
        roms_dir (Path): Path to the ROMs directory
        year (int): Game release year
        publisher (str): Game publisher
        
    Returns:
        bool: True if ROM exists, False otherwise
    """
    # Convert title to a filename-friendly format
    rom_filename = re.sub(r'[<>:"/\\|?*]', '', title)
    rom_filename = rom_filename.strip()
    
    # List all files in the ROM directory
    try:
        all_files = [f.name.lower() for f in roms_dir.iterdir() if f.is_file()]
    except Exception as e:
        print(f"Error accessing ROM directory: {e}")
        return False
    
    # Create variations of the filename
    variations = [
        rom_filename.lower(),                    # Original
        rom_filename.lower().replace(' ', ''),   # No spaces
        rom_filename.lower().replace(' ', '_'),  # Underscores
        rom_filename.lower().replace(' ', '-'),  # Hyphens
        rom_filename.lower().replace(' ', '.'),  # Dots
        rom_filename.lower().replace(' ', '').replace(':', '').replace('!', '').replace('?', ''),  # No special chars
        rom_filename.lower().replace(':', '').replace('!', '').replace('?', ''),  # Keep spaces, remove special chars
        rom_filename.lower().replace('the ', ''),  # Remove "the" prefix
        rom_filename.lower().replace('a ', ''),    # Remove "a" prefix
        rom_filename.lower().replace('an ', '')    # Remove "an" prefix
    ]
    
    # Check for common ROM extensions
    for ext in ['.zip', '.nes', '.7z']:
        for variation in variations:
            # Try with (USA) suffix
            if f"{variation} (usa){ext}" in all_files:
                if year and publisher:
                    rename_rom_file(f"{variation} (usa){ext}", year, publisher, roms_dir)
                return True
            # Try with (USA) suffix (uppercase)
            if f"{variation} (USA){ext}" in all_files:
                if year and publisher:
                    rename_rom_file(f"{variation} (USA){ext}", year, publisher, roms_dir)
                return True
            # Try without (USA) suffix
            if f"{variation}{ext}" in all_files:
                if year and publisher:
                    rename_rom_file(f"{variation}{ext}", year, publisher, roms_dir)
                return True
    
    return False

def print_games_table(games, name_filter=None):
    """
    Print a table of games.
    
    Args:
        games (list): List of dictionaries containing game information
        name_filter (str, optional): Substring to filter games by name
    """
    if not games:
        print("No games found.")
        return
    
    # Filter games by name if filter is provided
    if name_filter:
        games = [game for game in games if name_filter.lower() in game['title'].lower()]
        if not games:
            print(f"No games found matching '{name_filter}'")
            return
    
    # Path to ROMs directory
    roms_dir = Path(r"G:\Retro\Console\Nintendo\Nintendo NES\ROMS")
    
    # Print table header
    print(f"{'Year':<6} | {'Title':<50} | {'Publisher':<30} | {'Region':<15} | {'Status':<8}")
    print("-" * 120)
    
    # Print each game sorted by year and then by title
    for game in sorted(games, key=lambda x: (x.get('year', '99'), x.get('title', ''))):
        year = game.get('year', 'N/A')
        title = game.get('title', 'Unknown')
        publisher = game.get('publisher', 'Unknown')
        region = game.get('region', 'Unknown')
        
        # Check if ROM exists and rename if found
        #rom_exists = check_rom_exists(title, roms_dir, year, publisher)
        #status = "FOUND" if rom_exists else ""
        
        print(f"{year:<6} | {title[:50]:<50} | {publisher[:30]:<30} | {region[:15]:<15}")
    
    print(f"Total games: {len(games)}")

def create_html_table(games, name_filter=None):
    """
    Create an HTML file with the games table.
    
    Args:
        games (list): List of dictionaries containing game information
        name_filter (str, optional): Substring to filter games by name
    """
    # Filter games by name if filter is provided
    if name_filter:
        games = [game for game in games if name_filter.lower() in game['title'].lower()]
    
    # Create HTML content
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NES Games Collection</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f0f0f0;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #4CAF50;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            .status-found {
                color: #4CAF50;
                font-weight: bold;
            }
            .total-games {
                margin-top: 20px;
                text-align: right;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Nintendo Entertainment System Games</h1>
            <table>
                <tr>
                    <th>Year</th>
                    <th>Title</th>
                    <th>Publisher</th>
                    <th>Region</th>
                </tr>
    """
    
    # Add table rows
    for game in sorted(games, key=lambda x: (x.get('year', '99'), x.get('title', ''))):
        year = game.get('year', 'N/A')
        title = game.get('title', 'Unknown')
        publisher = game.get('publisher', 'Unknown')
        region = game.get('region', 'Unknown')
                
        html_content += f"""
                <tr>
                    <td>{year}</td>
                    <td>{title}</td>
                    <td>{publisher}</td>
                    <td>{region}</td>
                </tr>
        """
    
    # Close HTML
    html_content += f"""
            </table>
            <div class="total-games">Total games: {len(games)}</div>
        </div>
    </body>
    </html>
    """
    
    # Save HTML file
    output_file = Path("assets/nes_games_table.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nHTML table saved to: {output_file}")

def main():
    """
    Main entry point for the application.
    """
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='NES Games Collection Toolkit')
    parser.add_argument('--name', type=str, help='Filter games by name substring')
    args = parser.parse_args()
    
    # URL of the Nintendo Entertainment System games list
    url = "https://nintendo.fandom.com/wiki/List_of_Nintendo_Entertainment_System_games"
    
    # Path to save the downloaded HTML
    assets_dir = Path("assets")
    html_file = assets_dir / "nes_games_list_full.html"
    
    # Only download if file doesn't exist
    if not html_file.exists():
        print(f"Downloading games list from {url}...")
        download_webpage(url, html_file)
    else:
        print(f"Using existing games list from {html_file}")
    
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8', errors='replace') as f:
        html_content = f.read()
    
    # Extract games from 1985 to 1995
    games = extract_games_from_html(html_content, min_year=85, max_year=95)
    
    # Print the games table with optional name filter
    title = f"Nintendo Entertainment System Games - {len(games)} games"
    if args.name:
        title += f" (filtered by: '{args.name}')"
    print(title)
    print("=" * 90)
    print_games_table(games, args.name)
    
    # Create HTML table
    create_html_table(games, args.name)

if __name__ == "__main__":
    main() 