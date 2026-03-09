from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError
import uuid
from PIL import Image
from django.utils import timezone

def validate_image_size(image):
    max_size_kb = 2048  # 1 MB
    if image.size > max_size_kb * 2048:
        raise ValidationError(f"Image size should not exceed {max_size_kb} KB.")

class User(AbstractUser):
    
    CHOICES_ROLE = [
        ('admin', 'Admin'),
        ('viewer', 'Viewer'),
    ]

    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    role = models.CharField(max_length=10, choices=CHOICES_ROLE, default='viewer')
    profile_picture_url = models.ImageField(upload_to='profile_pictures/', validators=[validate_image_size], null=True, blank=True)

    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)\
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.profile_picture_url:
            img = Image.open(self.profile_picture_url.path)

            max_size = (300, 300)

            if img.height > 300 or img.width > 300:
                img.thumbnail(max_size)
                img.save(self.profile_picture_url.path)

    def __str__(self):
        return self.username
    
class Producer(models.Model):
    class Meta:
        constraints = [
            UniqueConstraint(
            Lower('name'),
            name='unique_producer_name_case_insensitive'
        )]

    producer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Studio(models.Model):
    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('studio_name'),
                name='unique_studio_name_case_insensitive'
            )
        ]
    studio_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    studio_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.studio_name

class Series(models.Model):

    ROLES_RATING = [
        ('g', 'G - All Ages'),
        ('pg', 'PG - Children'),
        ('pg_13', 'PG-13 - Teens 13 or older'),
        ('r', 'R - 17+ (violence & profanity)'),
    ]
        

    ROLES_STATUS = [
        ('ongoing', 'Ongoing'),
        ('finished', 'Finished'),
        ('upcoming', 'Upcoming'),
    ]

    ROLES_SEASON = [
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('fall', 'Fall'),
        ('winter', 'Winter'),
    ]

    series_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    alternate_title = models.CharField(max_length=255, null=True, blank=True)
    sypnosis = models.TextField()
    thumbnail_picture = models.ImageField(upload_to='series_thumbnails/', null=True, blank=True)
    total_episodes = models.IntegerField()
    season_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=ROLES_STATUS)
    genre = models.ManyToManyField('Genre', through='SeriesGenre')
    aired_start_date = models.DateField()
    aired_end_date = models.DateField(null=True, blank=True)
    premiered_season = models.CharField(max_length=10, choices=ROLES_SEASON)
    premiered_year = models.IntegerField()
    producer = models.ManyToManyField(Producer)
    studio = models.ManyToManyField(Studio)
    duration_minutes = models.IntegerField()
    score = models.DecimalField(max_digits=3, decimal_places=2)
    rating = models.CharField(max_length=10, choices=ROLES_RATING)
    is_published = models.BooleanField(default=False)
    is_published_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.is_published and not self.is_published_date:
            self.is_published_date = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Episode(models.Model):

    class Meta:
        unique_together = ('series', 'episode_number')
        

    episode_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    episode_number = models.IntegerField()
    episode_title = models.CharField(max_length=255)
    video_id = models.CharField(max_length=255)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.series.title} - Episode {self.episode_number}: {self.episode_title}"

class Watchlist(models.Model):
    watchlist_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.series.title}"
    
class WatchHistory(models.Model):
    watch_history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    progress_seconds = models.IntegerField(default=0)
    last_watched_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.series.title} - {self.episode.title} - {self.progress_seconds}s"
    
class Comment(models.Model):
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.episode.title} - {self.content[:20]}..."
    
class Genre(models.Model):

    genre_id = models.UUIDField(primary_key=True, default= uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class SeriesGenre(models.Model):
    class Meta:
        unique_together = ('series', 'genre')

    series_genre_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.series.title} - {self.genre.name}"
    
class ActivityLog(models.Model):
    activity_log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50)
    target_id = models.CharField(max_length=255, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class DeviceSession(models.Model):
    device_session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_token = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

class LoginLog(models.Model):
    login_log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.CharField(max_length=255, null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20)  # e.g., 'success', 'failure'
    timestamp = models.DateTimeField(auto_now_add=True)

class StreamingToken(models.Model):
    streaming_token_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    expired_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
