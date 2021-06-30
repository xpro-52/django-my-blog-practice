from django.test import TestCase
from django.contrib.auth.models import User
from unittest import skip
from django.utils import timezone

from .models import *
from .views import *


class RegistrationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        superuser = User.objects.create_superuser(username="test", password="testpass")
        post_title = ["test1", "test2", "test3"]
        post_text = ["test1text", "test2text", "test3text"]
        for i in range(3):
            Post.objects.create(author=superuser, 
                                published_date=timezone.now(),
                                title=post_title[i],
                                text=post_text[i],)
        Post.objects.create(author=superuser, published_date=None, title="draft", text="drafttext")
    
    def test_login(self):
        response = self.client.post(reverse("login"), {"username": "test", "password": "testpass"})
        self.assertRedirects(response, expected_url=reverse("blog:top"))
        response = self.client.get(reverse("blog:post-list"))
        self.assertEqual(response.context["post_list"].count(), 4)

    def test_logout(self):
        self.client.login(username="test", password="testpass")
        response = self.client.get(reverse("logout"))
        self.assertTemplateUsed(response, "registration/logged_out.html")
        response = self.client.get(reverse("blog:post-list"))
        self.assertEqual(response.context["post_list"].count(), 3)


class ProfileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        superuser = User.objects.create_superuser(username="test", password="testpass")
        Profile.objects.create(user=superuser,
                               public_name="test_publicname",
                               born="2021-6-1",
                               occupation="test_occupation",
                               github="https://github.com/",
                               text="test_text",)
    
    def test_display(self):
        response = self.client.get(reverse("blog:top"))
        self.assertEqual(response.context["profile"], Profile.objects.first())
        self.assertEqual(response.status_code, 200)

        self.client.login(username="test", password="testpass")
        response = self.client.get(reverse("blog:top"))
        self.assertEqual(response.context["profile"], Profile.objects.first())
        self.assertEqual(response.status_code, 200)
    
    def test_update_for_anonymous(self):
        response = self.client.get(reverse("blog:profile-update", kwargs={"pk": 1}))
        self.assertRedirects(response, expected_url=f"/accounts/login/?next=/blog/top/update/{1}/")

    def test_update_for_superuser(self):
        self.client.login(username="test", password="testpass")
        data = {
            "public_name": "update",
            "born": "2021-6-29",
            "occputation": "update",
            "github": "https://github.com/",
            "text": "update",
        }
        response = self.client.post(reverse("blog:profile-update", kwargs={"pk": 1}), data)
        self.assertRedirects(response, expected_url=reverse("blog:top"))
        self.assertTrue("update" == Profile.objects.first().public_name)


class PostTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        superuser = User.objects.create_superuser(username="test", password="testpass")
        post_title = ["test1", "test2", "test3"]
        post_text = ["test1text", "test2text", "test3text"]
        for i in range(3):
            Post.objects.create(author=superuser, 
                                published_date=timezone.now(),
                                title=post_title[i],
                                text=post_text[i],)
        Post.objects.create(author=superuser, published_date=None, title="draft", text="drafttext")

    def test_list_for_anonymous(self):
        response = self.client.get(reverse("blog:post-list"))
        self.assertTrue("draft" not in map(lambda post: post.title, response.context["post_list"]))
        self.assertEqual(response.context["post_list"].count(), 3)  # 4th is draft
        self.assertEqual(response.status_code, 200)

    def test_detail_for_anonymous(self):
        for i in range(1, 5):
            response = self.client.get(reverse("blog:post-detail", kwargs={"pk": i}))
            if i != 4:
                self.assertEqual(response.status_code, 200)
            else:
                self.assertEqual(response.status_code, 404)

    def test_create_update_delete_for_anonymous(self):
        response = self.client.get(reverse("blog:post-create"))
        self.assertRedirects(response, expected_url="/accounts/login/?next=/blog/post/create/")
        for i in range(1, 5):
            response = self.client.get(reverse("blog:post-update", kwargs={"pk": i}))
            self.assertRedirects(response, expected_url=f"/accounts/login/?next=/blog/post/update/{i}/")
            response = self.client.get(reverse("blog:post-delete", kwargs={"pk": i}))
            self.assertRedirects(response, expected_url=f"/accounts/login/?next=/blog/post/delete/{i}/")

    def test_list_for_superuser(self):
        self.client.login(username="test", password="testpass")
        response = self.client.get(reverse("blog:post-list"))
        self.assertEqual(response.context["post_list"].count(), 4)
        self.assertEqual(response.status_code, 200)

    def test_detail_for_superuser(self):
        self.client.login(username="test", password="testpass")
        for i in range(1, 5):
            response = self.client.get(reverse("blog:post-detail", kwargs={"pk": i}))
            self.assertEqual(response.status_code, 200)

    def test_create_for_superuser(self):
        self.client.login(username="test", password="testpass")
        data = {"author": User.objects.first().id,  # idを入れなければいけない
                "create_date": timezone.now(),
                "title": "create",
                "text": "createtext",
                "publish_flg": "on"}
        response = self.client.post(reverse("blog:post-create"), data)
        self.assertRedirects(response, expected_url=reverse("blog:post-list"))
        self.assertEqual(Post.objects.count(), 5)

        data["title"] = "create draft"
        data["publish_flg"] = ""
        response = self.client.post(reverse("blog:post-create"), data)
        self.assertTrue("create draft" in map(lambda post: post.title, Post.objects.all()))

    def test_update_for_superuser(self):
        self.client.login(username="test", password="testpass")
        data = {"author": User.objects.first().pk,
                "create_date": timezone.now(),
                "title": "update",
                "text": "updatetext",
                "publish_flg": "on"}
        response = self.client.post(reverse("blog:post-update", kwargs={"pk": 1}), data)
        self.assertRedirects(response, expected_url=reverse("blog:post-detail", kwargs={"pk": 1}))
        self.assertTrue("update" in map(lambda post: post.title, Post.objects.all()))

    def test_delete_for_superuser(self):
        self.client.login(username="test", password="testpass")
        response = self.client.post(reverse("blog:post-delete", kwargs={"pk": 1}))
        self.assertRedirects(response, expected_url=reverse("blog:post-list"))
        self.assertEqual(Post.objects.count(), 3)
        self.assertTrue("test1" not in map(lambda post: post.title, Post.objects.all()))



