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
                    if not row.get('Id'):  # Changed from isbn to Id
                        continue

                    # Convert price to decimal if exists, otherwise use default
                    try:
                        price = Decimal(str(row['Price'])) if row.get('Price') else Decimal('19.99')
                    except (ValueError, TypeError):
                        price = Decimal('19.99')

                    # Convert published date
                    try:
                        published_date = datetime.strptime(row['publishedDate'], '%Y-%m-%d').date() if row.get('publishedDate') else None
                    except (ValueError, TypeError):
                        published_date = None

                    # Convert ratings count
                    try:
                        ratings_count = int(float(row['ratingsCount'])) if row.get('ratingsCount') else 0
                    except (ValueError, TypeError):
                        ratings_count = 0

                    # Create or update book
                    book, created = Book.objects.update_or_create(
                        isbn=row['Id'],  # Using Id as ISBN
                        defaults={
                            'title': row['Title'].strip() if row.get('Title') else '',
                            'description': row['description'].strip() if row.get('description') else '',
                            'authors': row['authors'].strip() if row.get('authors') else '',
                            'image': row['image'] if row.get('image') else '',
                            'preview_link': row['previewLink'] if row.get('previewLink') else '',
                            'info_link': row['infoLink'] if row.get('infoLink') else '',
                            'publisher': row['publisher'].strip() if row.get('publisher') else '',
                            'published_date': published_date,
                            'price': price,
                            'stock': 10,  # Default stock
                            'language': 'EN',  # Default language
                            'ratings_count': ratings_count,
                            'average_rating': 0  # Will be calculated from reviews
                        }
                    )

                    if created:
                        books_created += 1
                    else:
                        books_updated += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error importing book: {row.get("Title", "Unknown")} - {str(e)}'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully imported books. Created: {books_created}, Updated: {books_updated}'
            )
        )