from django.db import models
from django.conf import settings
import uuid
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

# =========================
# カスタムユーザー
# =========================
class User(AbstractUser):
    unique_id = models.CharField(max_length=12, unique=True, blank=True)
    profile_bg = models.ImageField(upload_to='profile_bg/', blank=True, null=True)
    profile_icon = models.ImageField(upload_to='profile_icon/', blank=True, null=True)
    profile_message = models.TextField(blank=True, null=True)
    message_color = models.CharField(max_length=20, default="#ffffff")
    message_font = models.CharField(max_length=20, default="brush")

    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)


# =========================
# フレンド
# =========================
class Friend(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owner", on_delete=models.CASCADE)
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="friend", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


# =========================
# メッセージ
# =========================
class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sender", on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="receiver", on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


# =========================
# フォルダーアップロード
# =========================
def upload_to_folder(instance, filename):
    if not instance.folder_path:
        return f"uploads/{filename}"
    return f"uploads/{instance.folder_path}"

class UploadedFile(models.Model):
    file = models.FileField(upload_to=upload_to_folder)
    folder_path = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Report(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    report_date = models.DateField(null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        "ReportCategory",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reports",
    )

    class Meta:
        ordering = ["-created_at"]


class ReportCategory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="unique_report_category_per_user")
        ]

    def __str__(self):
        return self.name


class ReportFile(models.Model):
    report = models.ForeignKey(Report, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(upload_to="report_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


# =========================
# グループ（正しい定義）
# =========================
UserModel = get_user_model()

class Group(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)


# =========================
# プロフィール
# =========================
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)


# =========================
# スケジュール
# =========================
class Schedule(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    color = models.CharField(max_length=20, default="#12b88e")


# =========================
# グループ投票
# =========================
class Poll(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()


class PollQuestion(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    answer_type = models.CharField(max_length=10)  # "choice" or "text"


class PollChoice(models.Model):
    question = models.ForeignKey(PollQuestion, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)


class PollAnswer(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    question = models.ForeignKey(PollQuestion, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(PollChoice, null=True, blank=True, on_delete=models.SET_NULL)
    text = models.TextField(null=True, blank=True)


# =========================
# フレンド申請
# =========================
class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_requests", on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="received_requests", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
