from django.core.management.base import BaseCommand
import csv
from books.models import Book
from decimal import Decimal
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Import books from CSV file'

    def handle(self, *args, **kwargs):
        csv_path = 'bookstore_data.csv'
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found at {csv_path}'))
            return

        books_created = 0
        books_updated = 0

        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    if not row.get('isbn'):
                        continue

                    # Convert ratings to proper format
                    average_rating = float(row['average_rating']) if row['average_rating'] else 0
                    ratings_count = int(float(row['ratings_count'])) if row['ratings_count'] else 0
                    
                    # Get publication year
                    try:
                        pub_year = int(float(row['original_publication_year'])) if row['original_publication_year'] else None
                        pub_date = datetime(pub_year, 1, 1).date() if pub_year else None
                    except (ValueError, TypeError):
                        pub_date = None

                    # Create or update book
                    book, created = Book.objects.update_or_create(
                        isbn=row['isbn'],
                        defaults={
                            'title': row['title'].strip(),
                            'author': row['authors'].strip(),
                            'genre': 'Fiction',  # Default genre
                            'price': Decimal('19.99'),  # Default price
                            'stock': 10,  # Default stock
                            'summary': row.get('original_title', ''),
                            'cover_image': row['image_url'] if row['image_url'] else '',
                            'publication_date': pub_date,
                            'language': 'EN' if row.get('language_code', '').lower().startswith('en') else 'AR',
                            'average_rating': average_rating,
                            'total_ratings': ratings_count
                        }
                    )

                    if created:
                        books_created += 1
                    else:
                        books_updated += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error importing book: {row.get("title", "Unknown")} - {str(e)}'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully imported books. Created: {books_created}, Updated: {books_updated}'
            )
        )