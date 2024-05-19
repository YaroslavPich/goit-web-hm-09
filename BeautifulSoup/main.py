import json
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://quotes.toscrape.com'


def scrape_quotes():
	url = BASE_URL
	has_next_page = True
	response_quotes = []
	while has_next_page:
		response = requests.get(url)
		soup = BeautifulSoup(response.text, "lxml")
		quotes = soup.find_all("div", class_="quote")
		for q in quotes:
			tags = [tag.text for tag in q.find_all("a", class_="tag")]
			author = q.find("small", class_="author").text
			quote = q.find("span", class_="text").text
			response_quotes.append({
				"tags": tags,
				"author": author,
				"quote": quote
			})
		next_page = soup.find("li", class_="next")
		has_next_page = next_page is not None
		if has_next_page:
			next_page_url = next_page.find("a").attrs.get("href")
			url = urljoin(BASE_URL, next_page_url)
	return response_quotes


def scrape_authors():
	url = BASE_URL
	has_next_page = True
	response_authors = []
	set_authors_link = set()
	while has_next_page:
		response = requests.get(url)
		soup = BeautifulSoup(response.text, "lxml")
		quotes = soup.find_all("div", class_="quote")
		for q in quotes:
			authors_link = q.find("a").attrs.get("href")
			if authors_link not in set_authors_link:
				set_authors_link.add(authors_link)
				response_herro = requests.get(urljoin(url, authors_link))
				soup_author = BeautifulSoup(response_herro.text, "lxml")
				fullname = soup_author.find("h3", class_="author-title").text.strip()
				born_date = soup_author.find("span", class_="author-born-date").text.strip()
				born_location = soup_author.find("span", class_="author-born-location").text.strip()
				description = soup_author.find("div", class_="author-description").text.strip()
				response_authors.append({
					"fullname": fullname,
					"born_date": born_date,
					"born_location": born_location,
					"description": description
				})
		next_page = soup.find("li", class_="next")
		has_next_page = next_page is not None
		if has_next_page:
			next_page_url = next_page.find("a").attrs.get("href")
			url = urljoin(BASE_URL, next_page_url)
	return response_authors


if __name__ == '__main__':
	with open('quotes.json', 'w', encoding='utf-8') as fd:
		json.dump(scrape_quotes(), fd, ensure_ascii=False, indent=2)
	with open('authors.json', 'w', encoding='utf-8') as fd:
		json.dump(scrape_authors(), fd, ensure_ascii=False, indent=2)
