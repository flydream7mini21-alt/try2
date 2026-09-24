import datetime

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from .models import (
	Group, GroupMember, Poll, PollAnswer, PollChoice, PollQuestion,
	Report, ReportCategory, Schedule, UploadedFile, User,
)


class PollAnswerViewTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="poll-user", password="password")
		self.group = Group.objects.create(name="Test group", owner=self.user)
		GroupMember.objects.create(group=self.group, user=self.user, is_admin=True)

	def test_active_poll_shows_answer_form(self):
		now = timezone.now()
		poll = Poll.objects.create(
			group=self.group,
			title="Active poll",
			start_at=now - datetime.timedelta(minutes=5),
			end_at=now + datetime.timedelta(minutes=5),
		)
		PollQuestion.objects.create(poll=poll, text="Question", answer_type="text")

		self.client.force_login(self.user)
		response = self.client.get(reverse("poll_answer", args=[self.group.id, poll.id]))

		self.assertContains(response, 'name="answer_')
		self.assertContains(response, "回答を送信")
		self.assertContains(response, "回答は何回でもできます。もう一度送信すると、前回の回答に上書きされます。")
		self.assertContains(response, ".poll-answer-container .answer-notice")
		self.assertContains(response, "color: #d00 !important")
		self.assertContains(response, "font-size: 17px")
		self.assertContains(response, "white-space: nowrap")
		self.assertNotContains(response, "この投票は終了しています")

	def test_finished_poll_shows_closed_page(self):
		now = timezone.now()
		poll = Poll.objects.create(
			group=self.group,
			title="Finished poll",
			start_at=now - datetime.timedelta(minutes=10),
			end_at=now - datetime.timedelta(minutes=5),
		)

		self.client.force_login(self.user)
		response = self.client.get(reverse("poll_answer", args=[self.group.id, poll.id]))

		self.assertContains(response, "この投票は終了しています")

	def test_creating_poll_saves_questions_and_choices(self):
		now = timezone.now()
		local_now = timezone.localtime(now)

		self.client.force_login(self.user)
		response = self.client.post(
			reverse("poll_create", args=[self.group.id]),
			{
				"title": "Created poll",
				"start_at": (local_now - datetime.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M"),
				"end_at": (local_now + datetime.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M"),
				"questions[]": ["Where?", "Why?"],
				"answer_type[]": ["choice", "text"],
				"choices_0[]": ["Here", "There"],
			},
		)

		poll = Poll.objects.get(title="Created poll")
		question = PollQuestion.objects.get(poll=poll, text="Where?")
		self.assertRedirects(response, reverse("poll_list_active", args=[self.group.id]))
		self.assertEqual(PollQuestion.objects.filter(poll=poll).count(), 2)
		self.assertEqual(PollChoice.objects.filter(question=question).count(), 2)

		answer_response = self.client.get(
			reverse("poll_answer", args=[self.group.id, poll.id])
		)
		self.assertContains(answer_response, "Where?")
		self.assertContains(answer_response, "Here")
		self.assertContains(answer_response, "Why?")

	def test_resubmitting_replaces_answers_for_same_user(self):
		now = timezone.now()
		poll = Poll.objects.create(
			group=self.group,
			title="Replaceable poll",
			start_at=now - datetime.timedelta(minutes=5),
			end_at=now + datetime.timedelta(minutes=5),
		)
		question = PollQuestion.objects.create(
			poll=poll, text="Favorite place?", answer_type="text"
		)

		self.client.force_login(self.user)
		answer_url = reverse("poll_answer", args=[self.group.id, poll.id])
		self.client.post(answer_url, {f"answer_{question.id}": "First answer"})
		self.client.post(answer_url, {f"answer_{question.id}": "Latest answer"})

		answers = PollAnswer.objects.filter(poll=poll, user=self.user)
		self.assertEqual(answers.count(), 1)
		self.assertEqual(answers.get().text, "Latest answer")

		response = self.client.get(answer_url)
		self.assertContains(response, "Latest answer")

	def test_active_poll_list_shows_answer_status_for_current_user(self):
		now = timezone.now()
		answered_poll = Poll.objects.create(
			group=self.group,
			title="Answered poll",
			start_at=now - datetime.timedelta(minutes=5),
			end_at=now + datetime.timedelta(minutes=5),
		)
		unanswered_poll = Poll.objects.create(
			group=self.group,
			title="Unanswered poll",
			start_at=now - datetime.timedelta(minutes=5),
			end_at=now + datetime.timedelta(minutes=5),
		)
		question = PollQuestion.objects.create(
			poll=answered_poll, text="Question", answer_type="text"
		)
		PollAnswer.objects.create(
			poll=answered_poll,
			question=question,
			user=self.user,
			text="My answer",
		)

		self.client.force_login(self.user)
		response = self.client.get(
			reverse("poll_list_active", args=[self.group.id])
		)

		self.assertContains(response, "Answered poll")
		self.assertContains(response, "Unanswered poll")
		self.assertContains(response, "回答済み")
		self.assertContains(response, "未回答")

	def test_group_schedule_can_be_added(self):
		self.client.force_login(self.user)
		response = self.client.post(
			reverse("add_group_schedule", args=[self.group.id]),
			{
				"title": "Group event",
				"date": "2026-08-21",
				"start_time": "10:00",
				"end_time": "11:00",
				"color": "#12b88e",
			},
		)

		schedule = Schedule.objects.get(title="Group event")
		self.assertRedirects(response, reverse("group_calendar", args=[self.group.id]))
		self.assertEqual(schedule.group, self.group)
		self.assertEqual(schedule.start_time.strftime("%H:%M"), "10:00")


class FileManagerViewTests(TestCase):
	def test_folder_upload_keeps_relative_path(self):
		response = self.client.post(
			reverse("upload_multi"),
			{
				"files": SimpleUploadedFile("memo.txt", b"memo"),
				"paths": "project/docs/memo.txt",
			},
		)

		self.assertRedirects(response, reverse("file_manager"))
		self.assertEqual(UploadedFile.objects.get().folder_path, "project/docs/memo.txt")

	def test_zip_upload_is_available_as_a_single_file(self):
		response = self.client.post(
			reverse("upload_file"),
			{"file": SimpleUploadedFile("project.zip", b"zip-data")},
		)

		self.assertRedirects(response, reverse("file_manager"))
		stored_name = UploadedFile.objects.get().file.name
		self.assertTrue(stored_name.startswith("uploads/project"))
		self.assertTrue(stored_name.endswith(".zip"))

	def test_document_and_drawio_files_are_accepted(self):
		for filename in ("meeting.docx", "workflow.drawio"):
			response = self.client.post(
				reverse("upload_file"),
				{"file": SimpleUploadedFile(filename, b"file-data")},
			)
			self.assertRedirects(response, reverse("file_manager"))

		self.assertEqual(UploadedFile.objects.count(), 2)

class ReportViewTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="report-user", password="password")
		self.other_user = User.objects.create_user(username="other-user", password="password")
		self.client.force_login(self.user)

	def test_category_can_be_created_without_report_date_or_title(self):
		response = self.client.post(
			reverse("report") + "?mode=create",
			{"action": "create_category", "category_name": "業務"},
		)

		self.assertRedirects(response, reverse("report") + "?mode=create")
		self.assertTrue(ReportCategory.objects.filter(user=self.user, name="業務").exists())
		self.assertEqual(Report.objects.count(), 0)

	def test_report_uses_current_date_and_selected_user_category(self):
		category = ReportCategory.objects.create(user=self.user, name="業務")
		other_category = ReportCategory.objects.create(user=self.other_user, name="他人用")

		before = timezone.now()
		response = self.client.post(
			reverse("report"),
			{
				"title": "進捗レポート",
				"content": "本文",
				"category_id": category.id,
			},
		)
		report = Report.objects.get(title="進捗レポート")

		self.assertRedirects(response, reverse("report"))
		self.assertEqual(report.category, category)
		self.assertEqual(report.report_date, timezone.localdate())
		self.assertGreaterEqual(report.created_at, before)

		response = self.client.post(
			reverse("report"),
			{"title": "他人カテゴリ指定", "category_id": other_category.id},
		)
		self.assertIsNone(Report.objects.get(title="他人カテゴリ指定").category)

	def test_report_accepts_txt_save_mode_without_error(self):
		response = self.client.post(
			reverse("report"),
			{
				"title": "txt保存テスト",
				"content": "テキスト保存の本文",
				"save_mode": "txt",
			},
		)

		report = Report.objects.get(title="txt保存テスト")
		self.assertRedirects(response, reverse("report"))
		self.assertEqual(report.content, "テキスト保存の本文")

	def test_report_create_form_has_link_inserter_fields(self):
		response = self.client.get(reverse("report") + "?mode=create")

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'id="report-link-title"')
		self.assertContains(response, 'id="report-link-url"')
		self.assertContains(response, '本文にリンクを挿入')

	def test_report_list_supports_category_filter_and_grouped_pages(self):
		category_a = ReportCategory.objects.create(user=self.user, name="カテゴリA")
		category_b = ReportCategory.objects.create(user=self.user, name="カテゴリB")
		category_c = ReportCategory.objects.create(user=self.user, name="カテゴリC")
		category_d = ReportCategory.objects.create(user=self.user, name="カテゴリD")
		Report.objects.create(user=self.user, title="A1", content="A1本文", category=category_a)
		Report.objects.create(user=self.user, title="B1", content="B1本文", category=category_b)
		Report.objects.create(user=self.user, title="C1", content="C1本文", category=category_c)
		Report.objects.create(user=self.user, title="D1", content="D1本文", category=category_d)

		response = self.client.get(reverse("report") + "?mode=list")
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'name="category_id"')
		self.assertContains(response, 'カテゴリA')
		self.assertContains(response, 'report-category-grid')
		self.assertContains(response, 'report-list-pager')

		filter_response = self.client.get(reverse("report") + "?mode=list&category_id=" + str(category_b.id))
		self.assertContains(filter_response, 'カテゴリB')
		self.assertContains(filter_response, 'B1')
		self.assertNotContains(filter_response, 'D1')

	def test_report_url_title_is_rendered_as_link(self):
		for url in [
			"https://example.com/meeting",
			"www.example.com/meeting",
		]:
			report = Report.objects.create(user=self.user, title=url, content="本文")
			response = self.client.get(reverse("report") + "?id=" + str(report.id))
			self.assertContains(response, f'href="{url}"')
			self.assertContains(response, 'target="_blank"')

	def test_report_html_link_content_is_rendered_as_anchor(self):
		content = '<li><a href="https://example.com">証明書</a></li>'
		report = Report.objects.create(user=self.user, title="HTMLリンク", content=content)

		response = self.client.get(reverse("report") + "?id=" + str(report.id))
		self.assertContains(response, 'href="https://example.com"')
		self.assertContains(response, '>証明書<')
