"""
Test module for main.py
"""
import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import io
import sys

from src.main import main, download_webpage, parse_nes_games, print_games_table

def test_download_webpage_success():
    """
    Test the download_webpage function with a successful response.
    """
    # Mock the requests.get function
    with patch('requests.get') as mock_get:
        # Configure the mock
        mock_response = MagicMock()
        mock_response.content = b'<html>Test content</html>'
        mock_get.return_value = mock_response
        
        # Create a temporary file path
        test_file = 'test_output.html'
        
        try:
            # Call the function
            result = download_webpage('https://example.com', test_file)
            
            # Verify the function returned True
            assert result is True
            
            # Verify the file was created with the correct content
            assert os.path.exists(test_file)
            with open(test_file, 'rb') as f:
                content = f.read()
                assert content == b'<html>Test content</html>'
                
        finally:
            # Clean up the test file
            if os.path.exists(test_file):
                os.remove(test_file)

def test_download_webpage_failure():
    """
    Test the download_webpage function with a failed response.
    """
    # Mock the requests.get function to raise an exception
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception('Connection error')
        
        # Call the function
        result = download_webpage('https://example.com', 'test_output.html')
        
        # Verify the function returned False
        assert result is False

def test_parse_nes_games():
    """
    Test the parse_nes_games function.
    """
    # Sample HTML content
    html_content = """
    <html>
    <body>
    <table>
    <tr>
        <th>Title</th>
        <th>Publisher</th>
        <th>Release Date</th>
    </tr>
    <tr>
        <td>Super Mario Bros.</td>
        <td>Nintendo</td>
        <td>September 13, 1985</td>
    </tr>
    <tr>
        <td>The Legend of Zelda</td>
        <td>Nintendo</td>
        <td>February 21, 1986</td>
    </tr>
    </table>
    </body>
    </html>
    """
    
    # Mock the open function
    with patch('builtins.open', mock_open(read_data=html_content)):
        # Call the function
        games = parse_nes_games('dummy_path.html')
        
        # Verify the result
        assert len(games) == 2
        assert games[0]['title'] == 'Super Mario Bros.'
        assert games[0]['publisher'] == 'Nintendo'
        assert games[0]['year'] == '85'
        assert games[1]['title'] == 'The Legend of Zelda'
        assert games[1]['publisher'] == 'Nintendo'
        assert games[1]['year'] == '86'

def test_print_games_table():
    """
    Test the print_games_table function.
    """
    # Sample games data
    games = [
        {'title': 'Super Mario Bros.', 'publisher': 'Nintendo', 'year': '85'},
        {'title': 'The Legend of Zelda', 'publisher': 'Nintendo', 'year': '86'}
    ]
    
    # Capture stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    try:
        # Call the function
        print_games_table(games)
        
        # Get the output
        output = captured_output.getvalue()
        
        # Verify the output
        assert 'Year   | Title                                             | Publisher' in output
        assert '85     | Super Mario Bros.                                 | Nintendo' in output
        assert '86     | The Legend of Zelda                               | Nintendo' in output
    
    finally:
        # Reset stdout
        sys.stdout = sys.__stdout__

def test_main():
    """
    Test the main function with mocked dependencies.
    """
    # Mock the Path.exists method to return True
    with patch('pathlib.Path.exists', return_value=True), \
         patch('src.main.download_webpage') as mock_download, \
         patch('src.main.parse_nes_games') as mock_parse, \
         patch('src.main.print_games_table') as mock_print:
        
        # Configure the mocks
        mock_parse.return_value = [
            {'title': 'Super Mario Bros.', 'publisher': 'Nintendo', 'year': '85'}
        ]
        
        # Call the main function
        main()
        
        # Verify download_webpage was not called (file exists)
        mock_download.assert_not_called()
        
        # Verify parse_nes_games was called
        mock_parse.assert_called_once()
        
        # Verify print_games_table was called with the correct arguments
        mock_print.assert_called_once_with([
            {'title': 'Super Mario Bros.', 'publisher': 'Nintendo', 'year': '85'}
        ]) 