# ============================================================
#  認証・ホーム
# ============================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.views.generic import TemplateView
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime, date
import calendar

from .models import (
    User, Friend, FriendRequest, Message,
    Group, GroupMember,
    Schedule, UploadedFile, Report, ReportFile, ReportCategory
)

class memo(TemplateView):
    template_name="memo.html"


@login_required
def n_home(request):
    user = request.user
    month = int(request.GET.get("month", date.today().month))
    year = date.today().year

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdatescalendar(year, month)

    schedules = Schedule.objects.filter(date__year=year, date__month=month)

    schedule_map = {}
    for s in schedules:
        schedule_map.setdefault(s.date, []).append(s)

    return render(request, "n_home.html", {
        "month": month,
        "year": year,
        "days": month_days,
        "schedule_map": schedule_map,
        "prev_month": month - 1 if month > 1 else 12,
        "next_month": month + 1 if month < 12 else 1,
        "user": user
    })

# ログインページ
def home(request):
    return render(request, "login.html")

# サインアップ
from .forms import SignUpForm
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})

# ユーザー設定
@login_required
def user_settings(request):
    user = request.user

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.unique_id = request.POST.get("unique_id")

        password = request.POST.get("password")
        if password:
            user.set_password(password)
            user.save()
            update_session_auth_hash(request, user)
        else:
            user.save()

        return redirect("n_home")

    return render(request, "user_settings.html", {"user": user})


# ============================================================
#  フレンド機能
# ============================================================

@login_required
def friend_home(request):
    friends = Friend.objects.filter(user=request.user)
    groups = GroupMember.objects.filter(user=request.user)
    received_requests = FriendRequest.objects.filter(receiver=request.user, is_accepted=False)

    return render(request, "friend_home.html", {
        "friends": friends,
        "groups": groups,
        "received_requests": received_requests,
    })


@login_required
def friend_list(request):
    q = request.GET.get("q")
    friends = Friend.objects.filter(user=request.user)

    if q:
        friends = friends.filter(friend__unique_id__icontains=q)

    return render(request, "friend_list.html", {"friends": friends})


# フレンド申請
def send_friend_request(request):
    if request.method == "POST":
        unique_id = request.POST.get("unique_id")
        try:
            receiver = User.objects.get(unique_id=unique_id)
        except User.DoesNotExist:
            return render(request, "friend_request.html", {"error": "IDが存在しません"})

        if FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists():
            return render(request, "friend_request.html", {"error": "既に申請済みです"})

        if Friend.objects.filter(user=request.user, friend=receiver).exists():
            return render(request, "friend_request.html", {"error": "既にフレンドです"})

        FriendRequest.objects.create(sender=request.user, receiver=receiver)
        return redirect("friend_request")

    return redirect("friend_request")


# フレンド申請承認
def accept_friend_request(request, request_id):
    fr = FriendRequest.objects.get(id=request_id)

    Friend.objects.create(user=fr.receiver, friend=fr.sender)
    Friend.objects.create(user=fr.sender, friend=fr.receiver)

    fr.is_accepted = True
    fr.save()

    return redirect("friend_request")


def friend_request_page(request):
    received_requests = FriendRequest.objects.filter(receiver=request.user, is_accepted=False)
    sent_requests = FriendRequest.objects.filter(sender=request.user, is_accepted=False)

    return render(request, "friend_request.html", {
        "received_requests": received_requests,
        "sent_requests": sent_requests,
    })


@login_required
def add_friend(request):
    if request.method == "POST":
        target_id = request.POST.get("unique_id")
        try:
            target_user = User.objects.get(unique_id=target_id)
            Friend.objects.create(user=request.user, friend=target_user)
        except User.DoesNotExist:
            pass

    return redirect("friend_list")


# ============================================================
#  チャット機能
# ============================================================

@login_required
def chat_room(request, friend_id):
    friend = User.objects.get(id=friend_id)

    messages = Message.objects.filter(
        sender=request.user, receiver=friend
    ) | Message.objects.filter(
        sender=friend, receiver=request.user
    )
    messages = messages.order_by("created_at")

    return render(request, "chat_room.html", {
        "messages": messages,
        "friend": friend
    })


@login_required
def send_message(request, friend_id):
    friend = User.objects.get(id=friend_id)
    text = request.POST.get("text", "")
    file = request.FILES.get("file")

    Message.objects.create(
        sender=request.user,
        receiver=friend,
        text=text,
        file=file,
    )

    return redirect("chat_room", friend_id)


@login_required
def delete_message(request, message_id):
    msg = Message.objects.get(id=message_id)

    if msg.sender == request.user:
        msg.delete()

    return redirect("chat_room", friend_id=msg.receiver.id)


# ============================================================
#  グループ機能
# ============================================================

@login_required
def create_group(request):
    if request.method == "POST":
        name = request.POST.get("group_name")

        group = Group.objects.create(name=name, owner=request.user)
        GroupMember.objects.create(group=group, user=request.user, is_admin=True)

        return redirect("friend_home")

    return render(request, "group_create.html")


@login_required
def group_list(request):
    groups = GroupMember.objects.filter(user=request.user)
    return render(request, "group_list.html", {"groups": groups})


@login_required
def group_detail(request, group_id):
    group = Group.objects.get(id=group_id)
    members = GroupMember.objects.filter(group=group)
    schedules = Schedule.objects.filter(group=group)

    return render(request, "group_detail.html", {
        "group": group,
        "members": members,
        "schedules": schedules,
    })


@login_required
def add_group_member(request, group_id):
    group = Group.objects.get(id=group_id)
    member_id = request.POST.get("member_id")

    try:
        target = User.objects.get(unique_id=member_id)
        GroupMember.objects.create(group=group, user=target)
    except User.DoesNotExist:
        pass

    return redirect("group_detail", group_id)


# ============================================================
#  個人カレンダー
# ============================================================

@login_required
def calendar_view(request):
    year = int(request.GET.get("year", date.today().year))
    month = int(request.GET.get("month", date.today().month))

    cal = calendar.Calendar(firstweekday=6)
    days = cal.monthdatescalendar(year, month)

    schedules = Schedule.objects.filter(user=request.user, date__year=year, date__month=month)

    schedule_map = {}
    for s in schedules:
        schedule_map.setdefault(s.date, []).append(s)

    prev_month = month - 1 if month > 1 else 12
    prev_year = year - 1 if month == 1 else year

    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year

    return render(request, "calendar.html", {
        "year": year,
        "month": month,
        "days": days,
        "schedule_map": schedule_map,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
    })


@login_required
def add_schedule(request):
    if request.method == "POST":
        title = request.POST.get("title")
        date_str = request.POST.get("date")
        start_str = request.POST.get("start_time")
        end_str = request.POST.get("end_time")

        date_v = datetime.strptime(date_str, "%Y-%m-%d").date()
        start = datetime.strptime(start_str, "%H:%M").time() if start_str else None
        end = datetime.strptime(end_str, "%H:%M").time() if end_str else None

        Schedule.objects.create(
            title=title,
            date=date_v,
            start_time=start,
            end_time=end,
            user=request.user
        )

    return redirect("calendar")


@login_required
def delete_schedule(request, schedule_id):
    Schedule.objects.get(id=schedule_id).delete()
    return redirect("calendar")


@login_required
def update_schedule(request, schedule_id):
    schedule = Schedule.objects.get(id=schedule_id)

    if request.method == "POST":
        schedule.title = request.POST.get("title")
        schedule.date = datetime.strptime(request.POST.get("date"), "%Y-%m-%d").date()

        start = request.POST.get("start_time")
        end = request.POST.get("end_time")

        schedule.start_time = datetime.strptime(start, "%H:%M").time() if start else None
        schedule.end_time = datetime.strptime(end, "%H:%M").time() if end else None

        schedule.save()

    return redirect("calendar")




#グループ詳細
@login_required
def group_list(request):
    groups = GroupMember.objects.filter(user=request.user)
    return render(request, "group_list.html", {"groups": groups})


#グループ投票

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction

from .models import Poll, PollQuestion, PollChoice, PollAnswer, Group


@login_required
def poll_answer(request, group_id, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, group_id=group_id)

    now = timezone.now()

    if now < poll.start_at:
        return render(request, "poll_answer_closed.html", {
            "poll": poll,
            "message": "この投票はまだ開始していません。"
        })

    if now >= poll.end_at:
        return render(request, "poll_answer_closed.html", {
            "poll": poll,
            "message": "この投票は終了しています。"
        })

    questions = PollQuestion.objects.filter(poll=poll).prefetch_related("pollchoice_set")

    if request.method == "POST":
        user = request.user

        with transaction.atomic():
            PollAnswer.objects.filter(poll=poll, user=user).delete()

            for q in questions:
                if q.answer_type == "choice":
                    choice_id = request.POST.get(f"answer_{q.id}")
                    if choice_id:
                        PollAnswer.objects.create(
                            poll=poll,
                            question=q,
                            user=user,
                            choice_id=choice_id
                        )

                else:
                    text = request.POST.get(f"answer_{q.id}")
                    if text:
                        PollAnswer.objects.create(
                            poll=poll,
                            question=q,
                            user=user,
                            text=text
                        )

        return redirect("poll_list_active", group_id)

    existing_answers = {
        answer.question_id: answer
        for answer in PollAnswer.objects.filter(poll=poll, user=request.user)
    }
    for question in questions:
        question.existing_answer = existing_answers.get(question.id)

    return render(request, "poll_answer.html", {
        "poll": poll,
        "questions": questions,
        "existing_answers": existing_answers,
    })







@login_required
def poll_create(request, group_id):
    if request.method == "POST":
        title = request.POST["title"]

        # datetime-local → aware datetime（JST）
        start_at = timezone.make_aware(
            datetime.fromisoformat(request.POST["start_at"])
        )
        end_at = timezone.make_aware(
            datetime.fromisoformat(request.POST["end_at"])
        )

        poll = Poll.objects.create(
            group_id=group_id,
            title=title,
            start_at=start_at,
            end_at=end_at
        )

        questions = request.POST.getlist("questions[]")
        answer_types = request.POST.getlist("answer_type[]")

        for index, question_text in enumerate(questions):
            question = PollQuestion.objects.create(
                poll=poll,
                text=question_text,
                answer_type=answer_types[index]
            )

            if question.answer_type == "choice":
                choices = request.POST.getlist(f"choices_{index}[]")
                PollChoice.objects.bulk_create([
                    PollChoice(question=question, text=choice_text)
                    for choice_text in choices
                    if choice_text.strip()
                ])

        return redirect("poll_list_active", group_id)

    group = Group.objects.get(id=group_id)
    return render(request, "poll_create.html", {"group": group})

@login_required
def poll_result(request, poll_id):
    poll = Poll.objects.get(id=poll_id)
    questions = PollQuestion.objects.filter(poll=poll)

    for q in questions:
        if q.answer_type == "choice":
            choices = PollChoice.objects.filter(question=q)
            total = PollAnswer.objects.filter(question=q).count()

            for c in choices:
                count = PollAnswer.objects.filter(choice=c).count()
                c.percent = round((count / total) * 100, 1) if total > 0 else 0

            q.choices = choices

        else:
            q.text_answers = PollAnswer.objects.filter(question=q)

    return render(request, "poll_result.html", {
        "poll": poll,
        "questions": questions
    })

@login_required
def poll_list_finished(request, group_id):
    now = timezone.now()

    polls = Poll.objects.filter(
        group_id=group_id,
        end_at__lt=now
    )

    return render(request, "poll_list_finished.html", {
        "polls": polls,
        "group": Group.objects.get(id=group_id)
    })



from .models import Poll, PollQuestion, PollChoice, PollAnswer

from django.utils import timezone

from .models import Poll, Group
@login_required
def poll_list_active(request, group_id):
    now = timezone.now()

    polls = Poll.objects.filter(
        group_id=group_id,
        start_at__lte=now,
        end_at__gte=now
    )
    answered_poll_ids = set(
        PollAnswer.objects.filter(
            poll__in=polls,
            user=request.user,
        ).values_list("poll_id", flat=True)
    )

    # 締め切りまでの残り時間を計算
    for p in polls:
        p.has_answered = p.id in answered_poll_ids
        remaining = p.end_at - now
        hours = remaining.total_seconds() // 3600
        minutes = (remaining.total_seconds() % 3600) // 60
        p.remaining_time = f"{int(hours)}時間 {int(minutes)}分"

    return render(request, "poll_list_active.html", {
        "polls": polls,
        "group": Group.objects.get(id=group_id)
    })


@login_required
def poll_delete(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    # ★ グループ管理者だけ削除可能にしたい場合はここでチェック
    # if not GroupMember.objects.filter(group=poll.group, user=request.user, is_admin=True).exists():
    #     return redirect("poll_list_active", poll.group.id)

    poll.delete()
    return redirect("poll_list_active", poll.group.id)


@login_required
def poll_answer_closed(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    # 終了 or 未開始の判定は poll_answer と同じ
    now = timezone.now()

    if now < poll.start_at:
        message = "この投票はまだ開始していません。"
    elif now > poll.end_at:
        message = "この投票は終了しています。"
    else:
        message = "この投票は現在回答可能です。"

    return render(request, "poll_answer_closed.html", {
        "poll": poll,
        "message": message
    })


@login_required
def group_calendar_create(request):
    friends = Friend.objects.filter(user=request.user)

    if request.method == "POST":
        name = request.POST.get("group_name")

        # 複数入力欄から取得
        member_ids = request.POST.getlist("member_ids[]")

        # フレンド選択
        friend_ids = request.POST.getlist("friend_ids")

        group = Group.objects.create(name=name, owner=request.user)
        GroupMember.objects.create(group=group, user=request.user, is_admin=True)

        # 入力欄から追加
        for uid in member_ids:
            uid = uid.strip()
            if uid:
                try:
                    user = User.objects.get(unique_id=uid)
                    GroupMember.objects.get_or_create(group=group, user=user)
                except User.DoesNotExist:
                    pass

        # フレンドから追加
        for fid in friend_ids:
            try:
                user = User.objects.get(id=fid)
                GroupMember.objects.get_or_create(group=group, user=user)
            except User.DoesNotExist:
                pass

        return redirect("group_list")

    return render(request, "group_calendar_create.html", {"friends": friends})





@login_required
def update_group_schedule(request, schedule_id):
    schedule = Schedule.objects.get(id=schedule_id)

    # グループメンバー以外は編集不可
    if not GroupMember.objects.filter(group=schedule.group, user=request.user).exists():
        return redirect("group_calendar", schedule.group.id)

    if request.method == "POST":
        schedule.title = request.POST.get("title")
        schedule.date = request.POST.get("date")
        schedule.start_time = request.POST.get("start_time")
        schedule.end_time = request.POST.get("end_time")
        schedule.color = request.POST.get("color")
        schedule.save()

        return redirect("group_calendar", schedule.group.id)

    return render(request, "update_group_schedule.html", {"schedule": schedule})

# ============================================================
#  グループカレンダー（色選択6色）
# ============================================================

@login_required
def group_calendar(request, group_id):
    group = Group.objects.get(id=group_id)

    # メンバー以外は閲覧不可
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        return redirect("friend_home")

    year = int(request.GET.get("year", date.today().year))
    month = int(request.GET.get("month", date.today().month))

    cal = calendar.Calendar(firstweekday=6)
    days = cal.monthdatescalendar(year, month)

    schedules = Schedule.objects.filter(group=group, date__year=year, date__month=month)

    schedule_map = {}
    for s in schedules:
        schedule_map.setdefault(s.date, []).append(s)

    prev_month = month - 1 if month > 1 else 12
    prev_year = year - 1 if month == 1 else year

    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year

    return render(request, "group_calendar.html", {
        "group": group,
        "year": year,
        "month": month,
        "days": days,
        "schedule_map": schedule_map,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
    })


@login_required
def add_group_schedule(request, group_id):
    group = Group.objects.get(id=group_id)

    if request.method == "POST":
        title = request.POST.get("title")
        date_str = request.POST.get("date")
        start_str = request.POST.get("start_time")
        end_str = request.POST.get("end_time")
        color = request.POST.get("color")  # ★ 6色対応

        date_v = datetime.strptime(date_str, "%Y-%m-%d").date()
        start = datetime.strptime(start_str, "%H:%M").time() if start_str else None
        end = datetime.strptime(end_str, "%H:%M").time() if end_str else None

        Schedule.objects.create(
            title=title,
            date=date_v,
            start_time=start,
            end_time=end,
            group=group,
            color=color
        )

        # ★ group_detail と group_calendar の両方に対応
        if "from_detail" in request.POST:
            return redirect("group_detail", group_id)

        return redirect("group_calendar", group_id)

    return redirect("group_calendar", group_id)


@login_required
def delete_group_schedule(request, schedule_id):
    s = Schedule.objects.get(id=schedule_id)

    if GroupMember.objects.filter(group=s.group, user=request.user).exists():
        s.delete()

    return redirect("group_calendar", s.group.id)


# ============================================================
#  ファイル管理
# ============================================================

from django.http import FileResponse, Http404
from pathlib import PurePosixPath

class FileManagerView(TemplateView):
    template_name = "file_manager.html"

    def get(self, request):
        files = UploadedFile.objects.all().order_by('-uploaded_at')

        date_v = request.GET.get("date")
        if date_v:
            files = files.filter(uploaded_at__date=date_v)

        return render(request, self.template_name, {"files": files})


def upload_file(request):
    if request.method == "POST":
        f = request.FILES['file']
        UploadedFile.objects.create(file=f, folder_path="")
    return redirect("file_manager")


def upload_multi(request):
    if request.method == "POST":
        files = request.FILES.getlist("files")
        paths = request.POST.getlist("paths")
        for index, f in enumerate(files):
            relative_path = paths[index] if index < len(paths) else f.name
            relative_path = str(PurePosixPath(relative_path.replace("\\", "/")))
            if relative_path in {".", ""} or relative_path.startswith("../"):
                relative_path = PurePosixPath(f.name).name
            UploadedFile.objects.create(file=f, folder_path=relative_path)
    return redirect("file_manager")


def delete_file(request, pk):
    file_obj = UploadedFile.objects.get(pk=pk)
    file_obj.file.delete()
    file_obj.delete()
    return redirect("file_manager")


def delete_all_files(request):
    for f in UploadedFile.objects.all():
        f.file.delete()
        f.delete()
    return redirect("file_manager")


def download_file(request, pk):
    try:
        file_obj = UploadedFile.objects.get(pk=pk)
        return FileResponse(file_obj.file.open('rb'), as_attachment=True)
    except UploadedFile.DoesNotExist:
        raise Http404("ファイルがありません")


# ============================================================
#  プロフィール
# ============================================================

@login_required
def friend_profile(request):
    return render(request, "friend_profile.html", {"user": request.user})


@login_required
def update_profile_bg(request):
    if request.method == "POST":
        bg = request.FILES.get("profile_bg")
        if bg:
            request.user.profile_bg = bg
            request.user.save()
    return redirect("friend_profile")


@login_required
def update_profile_icon(request):
    if request.method == "POST":
        icon = request.FILES.get("profile_icon")
        if icon:
            request.user.profile_icon = icon
            request.user.save()
    return redirect("friend_profile")


@login_required
def update_profile_message(request):
    if request.method == "POST":
        user = request.user
        user.profile_message = request.POST.get("profile_message")
        user.message_color = request.POST.get("message_color")
        user.message_font = request.POST.get("message_font")
        user.save()
    return redirect("friend_profile")





@login_required
def report(request):
    if request.method == "POST":
        action = request.POST.get("action", "save_report")
        if action == "create_category":
            category_name = request.POST.get("category_name", "").strip()
            if category_name:
                ReportCategory.objects.get_or_create(
                    user=request.user,
                    name=category_name,
                )
            return redirect(f"{reverse('report')}?mode=create")

        if action == "update_report":
            report_id = request.POST.get("report_id")
            report_obj = get_object_or_404(Report, id=report_id, user=request.user)
            title = request.POST.get("title", "").strip()
            if not title:
                return redirect(f"{reverse('report')}?id={report_obj.id}")
            report_obj.title = title
            report_obj.content = request.POST.get("content", "")
            report_obj.category = ReportCategory.objects.filter(
                user=request.user,
                id=request.POST.get("category_id"),
            ).first()
            report_obj.save()
            return redirect(f"{reverse('report')}?id={report_obj.id}")

        if action == "delete_report":
            report_id = request.POST.get("report_id")
            report_obj = get_object_or_404(Report, id=report_id, user=request.user)
            report_obj.delete()
            return redirect("report")

        report_obj = Report.objects.create(
            user=request.user,
            report_date=timezone.localdate(),
            title=request.POST.get("title", "").strip(),
            content=request.POST.get("content", ""),
            category=ReportCategory.objects.filter(
                user=request.user,
                id=request.POST.get("category_id"),
            ).first(),
        )
        for uploaded_file in request.FILES.getlist("files"):
            ReportFile.objects.create(report=report_obj, file=uploaded_file)
        return redirect("report")

    reports = Report.objects.filter(user=request.user).prefetch_related("files")
    categories = ReportCategory.objects.filter(user=request.user)
    mode = request.GET.get("mode", "home")
    report_id = request.GET.get("id")
    selected_report = None
    selected_category_id = request.GET.get("category_id")
    selected_category = None
    if selected_category_id:
        selected_category = get_object_or_404(categories, id=selected_category_id)
    if report_id:
        selected_report = get_object_or_404(reports, id=report_id)
        mode = "detail"
    if mode not in {"home", "create", "list", "detail"}:
        mode = "home"

    visible_categories = list(categories)
    if selected_category is not None:
        visible_categories = [selected_category]

    category_page = request.GET.get("category_page", "1")
    try:
        category_page = max(1, int(category_page))
    except (TypeError, ValueError):
        category_page = 1

    category_page_size = 3
    total_category_pages = max(1, (len(visible_categories) + category_page_size - 1) // category_page_size)
    if category_page > total_category_pages:
        category_page = total_category_pages

    category_page_start = (category_page - 1) * category_page_size
    category_page_end = category_page_start + category_page_size
    paged_categories = visible_categories[category_page_start: category_page_end]

    category_reports = {}
    for category in paged_categories:
        category_reports[category.id] = list(reports.filter(category=category))

    list_base_url = reverse("report") + "?mode=list"
    if selected_category_id:
        list_base_url += f"&category_id={selected_category_id}"

    return render(request, "report.html", {
        "reports": reports,
        "recent_reports": reports[:3],
        "report_count": reports.count(),
        "report_file_count": ReportFile.objects.filter(report__user=request.user).count(),
        "mode": mode,
        "selected_report": selected_report,
        "categories": categories,
        "selected_category": selected_category,
        "selected_category_id": selected_category_id,
        "visible_categories": paged_categories,
        "category_reports": category_reports,
        "category_page": category_page,
        "total_category_pages": total_category_pages,
        "prev_category_page": max(1, category_page - 1),
        "next_category_page": min(total_category_pages, category_page + 1),
        "list_base_url": list_base_url,
    })
    
    

#===============
#メール全体
#===============
class meilAll(TemplateView):
    template_name="meil_ALL.html"