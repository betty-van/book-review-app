import requests
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Ofp1GU7uUbEelrn6ZrT9w", "isbns": "9781632168146"})
print(res.json())