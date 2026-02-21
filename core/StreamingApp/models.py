from django.db import models
import uuid

class User(models.Model):
    CHOICES_ROLE = [
        ('admin', 'Admin'),
        ('viewer', 'Viewer'),
        ('guest', 'Guest'),
    ]

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=CHOICES_ROLE)
    is_active = models.BooleanField(default=True)
    failed_login_attempts = models.IntegerField(default=0)
    last_login_attempt = models.DateTimeField(null=True, blank=True)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_picture_url = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return self.username

class Movie(models.Model):
    movie_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    duration = models.IntegerField(help_text="Duration in minutes")
    thumbnail_url = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    video_id = models.CharField(max_length=255) #dilanjut di html
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Watchlist(models.Model):
    watchlist_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user_id.username} - {self.movie_id.title}"
    
class WatchHistory(models.Model):
    watch_history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    progress_seconds = models.IntegerField(default=0)
    last_watched_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_id.username} - {self.movie_id.title} - {self.progress_seconds}s"
    
class Comment(models.Model):
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_id.username} - {self.movie_id.title} - {self.content[:20]}..."
    
class Genre(models.Model):
    CHOICES_GENRE = [
        ('action', 'Action'),
        ('comedy', 'Comedy'),
        ('drama', 'Drama'),
        ('horror', 'Horror'),
        ('sci-fi', 'Sci-Fi'),
        ('romance', 'Romance'),
        ('thriller', 'Thriller'),
        ('animation', 'Animation'),
        ('documentary', 'Documentary'),
        ('fantasy', 'Fantasy'),
        ('isekai', 'Isekai'),
        ('mecha', 'Mecha'),
        ('school', 'School'),
    ]
    genre_id = models.UUIDField(primary_key=True, default= uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, choices=CHOICES_GENRE, unique=True)

class MovieGenre(models.Model):
    class Meta:
        unique_together = ('movie_id', 'genre_id')

    movie_genre_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre_id = models.ForeignKey(Genre, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.movie_id.title} - {self.genre_id.name}"

