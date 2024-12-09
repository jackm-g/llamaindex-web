import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def url_to_filename(url):
    # Convert a URL path into a safe filename
    parsed = urlparse(url)
    path = parsed.path
    if not path or path == '/':
        # For the homepage
        return "index.html"
    # Replace any slashes with underscores
    filename = path.strip("/").replace("/", "_") + ".html"
    return filename

def get_available_filename(base_dir, filename):
    # Ensure that if there's a filename conflict, we generate a unique name
    if not os.path.exists(os.path.join(base_dir, filename)):
        return filename
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(base_dir, f"{base}_{counter}{ext}")):
        counter += 1
    return f"{base}_{counter}{ext}"

def scrape_domain(domain, output_dir):
    # Normalize domain by ensuring it starts with http/https
    if not domain.startswith("http://") and not domain.startswith("https://"):
        domain = "http://" + domain

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    try:
        response = requests.get(domain, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {domain}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Collect all internal links
    internal_links = set()
    domain_netloc = urlparse(domain).netloc
    for link_tag in soup.find_all('a', href=True):
        href = link_tag['href']
        absolute_url = urljoin(domain, href)
        if urlparse(absolute_url).netloc == domain_netloc:
            internal_links.add(absolute_url)

    # Also add the homepage itself
    internal_links.add(domain)

    # Download each page and save it
    for link in internal_links:
        try:
            page_response = requests.get(link, timeout=10)
            page_response.raise_for_status()

            # Parse the HTML and extract body content
            page_soup = BeautifulSoup(page_response.text, "html.parser")
            body_content = page_soup.body

            # If body exists, get its text content
            content_to_save = body_content.get_text(separator='\n', strip=True) if body_content else ""

            # Create a filename based on the URL
            filename = url_to_filename(link)
            filename = get_available_filename(output_dir, filename)
            file_path = os.path.join(output_dir, filename)

            # Save only the body content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content_to_save)
            print(f"Saved body content: {link} -> {file_path}")
        except requests.RequestException as e:
            print(f"Error downloading {link}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scrape.py <domain> <output_directory>")
        sys.exit(1)

    domain = sys.argv[1]
    output_dir = sys.argv[2]
    scrape_domain(domain, output_dir)
