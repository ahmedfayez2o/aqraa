from mongoengine import Document, StringField, DecimalField, URLField

class Book(Document):
    title = StringField(max_length=255, required=True)
    author = StringField(max_length=255, required=True)
    genre = StringField(max_length=100)
    isbn = StringField(max_length=20, unique=True)
    price = DecimalField(precision=2, required=True)
    summary = StringField()
    cover_image = URLField()

    meta = {'collection': 'books'}

    def __str__(self):
        return self.title
