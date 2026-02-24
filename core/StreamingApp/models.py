from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
import uuid

class User(AbstractUser):
    CHOICES_ROLE = [
        ('admin', 'Admin'),
        ('viewer', 'Viewer'),
    ]

    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    role = models.CharField(max_length=10, choices=CHOICES_ROLE, default='viewer')
    profile_picture_url = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    total_episodes = models.IntegerField()
    season_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=ROLES_STATUS)
    aired_start_date = models.DateField()
    aired_end_date = models.DateField(null=True, blank=True)
    premiered_season = models.CharField(max_length=10, choices=ROLES_SEASON)
    premiered_year = models.IntegerField()
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    duration_minutes = models.IntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title

class Episode(models.Model):

    class Meta:
        unique_together = ('series', 'episode_number')

    episode_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    episode_number = models.IntegerField()
    title = models.CharField(max_length=255)
    video_id = models.CharField(max_length=255)
    view_count = models.IntegerField(default=0)
    duration_seconds = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Watchlist(models.Model):
    watchlist_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.series.title}"
    
class WatchHistory(models.Model):
    watch_history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    progress_seconds = models.IntegerField(default=0)
    last_watched_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.episode.title} - {self.progress_seconds}s"
    
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

    CHOICES_GENRE = [
        ('action', 'Action'),
        ('adventure', 'Adventure'),
        ('cars', 'Cars'),
        ('comedy', 'Comedy'),
        ('dementia', 'Dementia'),
        ('demons', 'Demons'),
        ('drama', 'Drama'),
        ('ecchi', 'Ecchi'),
        ('fantasy', 'Fantasy'),
        ('game', 'Game'),
        ('harem', 'Harem'),
        ('historical', 'Historical'),
        ('horror', 'Horror'),
        ('isekai', 'Isekai'),
        ('josei', 'Josei'),
        ('kids', 'Kids'),
        ('magic', 'Magic'),
        ('martial_arts', 'Martial Arts'),
        ('mecha', 'Mecha'),
        ('military', 'Military'),
        ('music', 'Music'),
        ('mystery', 'Mystery'),
        ('parody', 'Parody'),
        ('police', 'Police'),
        ('psychological', 'Psychological'),
        ('romance', 'Romance'),
        ('samurai', 'Samurai'),
        ('school', 'School'),
        ('sci-fi', 'Sci-Fi'),
        ('seinen', 'Seinen'),
        ('shoujo', 'Shoujo'),
        ('shounen', 'Shounen'),
        ('shoujo_ai', 'Shoujo Ai'),
        ('shounen_ai', 'Shounen Ai'),
        ('slice_of_life', 'Slice of Life'),
        ('space', 'Space'),
        ('sports', 'Sports'),
        ('super_power', 'Super Power'),
        ('supernatural', 'Supernatural'),
        ('thriller', 'Thriller'),
        ('vampire', 'Vampire'),
        ('yaoi', 'Yaoi'),
        ('yuri', 'Yuri'),
    ]
    genre_id = models.UUIDField(primary_key=True, default= uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, choices=CHOICES_GENRE, unique=True)

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
    
