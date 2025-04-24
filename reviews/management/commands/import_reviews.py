from django.core.management.base import BaseCommand
import csv
from reviews.models import Review
from books.models import Book
from django.contrib.auth import get_user_model
from datetime import datetime
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Import reviews from CSV file'

    def handle(self, *args, **kwargs):
        csv_path = 'bookstore_data.csv'
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found at {csv_path}'))
            return

        reviews_created = 0
        reviews_skipped = 0

        # Make sure we have at least one user in the system
        default_user, created = User.objects.get_or_create(
            username='default_user',
            defaults={
                'email': 'default@example.com',
                'is_active': True
            }
        )

        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    # Skip if no review text or book ID
                    if not row.get('review/text') or not row.get('Id'):
                        reviews_skipped += 1
                        continue

                    # Try to get the book
                    try:
                        book = Book.objects.get(isbn=row['Id'])
                    except Book.DoesNotExist:
                        reviews_skipped += 1
                        continue

                    # Convert review time from timestamp
                    try:
                        review_time = datetime.fromtimestamp(float(row['review/time']))
                    except (ValueError, TypeError):
                        review_time = datetime.now()

                    # Convert score
                    try:
                        score = int(float(row['review/score']))
                    except (ValueError, TypeError):
                        score = 3  # Default score if invalid

                    # Create the review
                    review = Review.objects.create(
                        user=default_user,
                        book=book,
                        profile_name=row.get('profileName', 'Anonymous'),
                        helpfulness=row.get('review/helpfulness', ''),
                        score=score,
                        time=review_time,
                        summary=row.get('review/summary', '')[:255],  # Truncate if too long
                        text=row.get('review/text', '')
                    )

                    reviews_created += 1

                    # Update book's rating
                    book.update_rating(score)

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error importing review for book {row.get("Id", "Unknown")}: {str(e)}'
                        )
                    )
                    reviews_skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully imported reviews. Created: {reviews_created}, Skipped: {reviews_skipped}'
            )
        )