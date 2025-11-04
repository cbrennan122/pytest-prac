import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from unittest.mock import patch
import requests

def get_status(url):
    response = requests.get(url)
    return response.status_code

@patch("requests.get")
def test_get_status_ok(mock_get):
    
    mock_get.return_value.status_code = 200
    assert get_status("https://example.com") == 200

@patch("requests.get")
def test_get_status_not_found(mock_get):
    mock_get.return_value.status_code = 404
    assert get_status("https://example.com/404") == 404
