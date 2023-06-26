from flask import Flask, redirect, url_for, render_template, request
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    author = request.form.get("author")

    source = 'https://www.googleapis.com/books/v1/volumes'
    params = {
        'q': f'inauthor:"{author}"',
        'maxResults': 40,
        'langRestrict': 'en'
    }

    books = set()
    results = []

    while True:
        response = requests.get(source, params=params)
        data = response.json()

        for item in data.get('items', []):
            volume_info = item.get('volumeInfo')
            if volume_info and 'authors' in volume_info and author in volume_info['authors']:
                title = volume_info.get('title', '')
                if all(title not in book_title for book_title in books):
                    authors = volume_info.get('authors', [])
                    publisher = volume_info.get('publisher', '')
                    description = volume_info.get('description', '')
                    language = volume_info.get('language', '')

                    if language.lower() == 'en':
                        book_id = item.get('id', '')
                        ratings = get_book_ratings(book_id)
                        if ratings:
                            average_rating = ratings['averageRating']
                            ratings_count = ratings['ratingsCount']
                        else:
                            average_rating = 'N/A'
                            ratings_count = 0

                        book_info = {
                            'title': title,
                            'authors': authors,
                            'publisher': publisher,
                            'description': description,
                            'average_rating': average_rating,
                            'ratings_count': ratings_count
                        }
                        results.append(book_info)
                        books.add(title)

        if 'nextPageToken' in data:
            params['pageToken'] = data['nextPageToken']
        else:
            break

    return render_template("search.html", author=author, results=results)

def get_book_ratings(book_id):
    url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    response = requests.get(url)
    data = response.json()

    if "averageRating" in data["volumeInfo"]:
        average_rating = data["volumeInfo"]["averageRating"]
        ratings_count = data["volumeInfo"]["ratingsCount"]
        return {'averageRating': average_rating, 'ratingsCount': ratings_count}
    else:
        return None

if __name__ == "__main__":
    app.run()
