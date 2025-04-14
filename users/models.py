from mongoengine import Document, StringField, EmailField, ImageField, BooleanField, DateTimeField

class CustomUser(Document):
    username = StringField(max_length=150, unique=True, required=True)
    email = EmailField(unique=True, required=True)
    password = StringField(required=True)
    first_name = StringField(max_length=150)
    last_name = StringField(max_length=150)
    profile_picture = StringField()  # Store the path to the image
    bio = StringField()
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    date_joined = DateTimeField()

    meta = {'collection': 'users'}

    def __str__(self):
        return self.username
