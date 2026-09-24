from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # ============================
    # 認証
    # ============================
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("signup/", views.signup, name="signup"),
    path("settings/", views.user_settings, name="user_settings"),

    # ============================
    # ホーム
    # ============================
    path("n_home/", views.n_home, name="n_home"),
    path("memo/", views.memo.as_view(), name="memo"),

    # ============================
    # ファイル管理
    # ============================
    path("file_manager/", views.FileManagerView.as_view(), name="file_manager"),
    path("upload_file/", views.upload_file, name="upload_file"),
    path("upload_multi/", views.upload_multi, name="upload_multi"),
    path("delete_file/<int:pk>/", views.delete_file, name="delete_file"),
    path("delete_all/", views.delete_all_files, name="delete_all"),
    path("download_file/<int:pk>/", views.download_file, name="download_file"),

    # ============================
    # 個人カレンダー
    # ============================
    path("calendar/", views.calendar_view, name="calendar"),
    path("add_schedule/", views.add_schedule, name="add_schedule"),
    path("schedule/delete/<int:schedule_id>/", views.delete_schedule, name="delete_schedule"),
    path("schedule/update/<int:schedule_id>/", views.update_schedule, name="update_schedule"),
    
    # ============================
    # グループカレンダー
    # ============================
    path("group_list/", views.group_list, name="group_list"),
    path("group_calendar_create/", views.group_calendar_create, name="group_calendar_create"),
    path("group/schedule/update/<int:schedule_id>/", views.update_group_schedule, name="update_group_schedule"),
    #グループ投票
    path("group/<int:group_id>/polls/active/", views.poll_list_active, name="poll_list_active"),
    path("group/<int:group_id>/poll/<int:poll_id>/answer/", views.poll_answer, name="poll_answer"),
    
    path("group/<int:group_id>/polls/finished/", views.poll_list_finished, name="poll_list_finished"),
    path("poll/<int:poll_id>/result/", views.poll_result, name="poll_result"),
    path("group/<int:group_id>/poll/create/", views.poll_create, name="poll_create"),
    path("poll/delete/<int:poll_id>/", views.poll_delete, name="poll_delete"),
    path("poll/closed/<int:poll_id>/", views.poll_answer_closed, name="poll_answer_closed"),




    path("group/calendar/<int:group_id>/", views.group_calendar, name="group_calendar"),
    path("group/<int:group_id>/", views.group_detail, name="group_detail"),
    path("group/schedule/add/<int:group_id>/", views.add_group_schedule, name="add_group_schedule"),
    path("group/schedule/delete/<int:schedule_id>/", views.delete_group_schedule, name="delete_group_schedule"),

    # ============================
    # フレンド機能
    # ============================
    path("friends/", views.friend_list, name="friend_list"),
    path("friends/add/", views.add_friend, name="add_friend"),
    path("friend_home/", views.friend_home, name="friend_home"),

    # フレンド申請
    path("friend_request/", views.friend_request_page, name="friend_request"),
    path("send_friend_request/", views.send_friend_request, name="send_friend_request"),
    path("accept_friend_request/<int:request_id>/", views.accept_friend_request, name="accept_friend_request"),

    # ============================
    # チャット
    # ============================
    path("chat/<int:friend_id>/", views.chat_room, name="chat_room"),
    path("chat/send/<int:friend_id>/", views.send_message, name="send_message"),
    path("delete_message/<int:message_id>/", views.delete_message, name="delete_message"),

    # ============================
    # グループ機能
    # ============================
    path("create_group/", views.create_group, name="create_group"),
    path("groups/create/", views.create_group, name="group_create"),
    path("groups/<int:group_id>/add_member/", views.add_group_member, name="add_group_member"),

    # ============================
    # プロフィール
    # ============================
    path("friend_profile/", views.friend_profile, name="friend_profile"),
    path("profile/update_bg/", views.update_profile_bg, name="update_profile_bg"),
    path("profile/update_icon/", views.update_profile_icon, name="update_profile_icon"),
    path("profile/update_message/", views.update_profile_message, name="update_profile_message"),
    
    # ============================
    # レポート
    # ============================
    path("report/", views.report, name="report"),
    # ============================
    # メール全般
    # ============================
    path("meil_ALL/",views.meilAll.as_view(),name="meil"),
    
]

# メディアファイル
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
