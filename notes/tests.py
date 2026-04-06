from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Note

LOCMEM_CACHE = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


class NoteListCreateTests(APITestCase):
    def setUp(self):
        self.url = reverse("note-list", kwargs={"version": "v1"})
        self.valid_payload = {"title": "Test Note", "content": "Test content"}
        self.user = User.objects.create_user(username="testuser", password="<PASSWORD>")
        self.client.force_authenticate(user=self.user)

    def test_list_notes_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

    def test_list_notes_returns_all(self):
        Note.objects.create(title="Note 1", content="Content 1", creator=self.user)
        Note.objects.create(title="Note 2", content="Content 2", creator=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_create_note_success(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(response.data["title"], "Test Note")
        self.assertEqual(response.data["content"], "Test content")
        self.assertIn("id", response.data)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_create_note_missing_title(self):
        response = self.client.post(self.url, {"content": "No title"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_create_note_missing_content(self):
        response = self.client.post(self.url, {"title": "No content"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("content", response.data)

    def test_create_note_empty_payload(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_note_title_too_long(self):
        response = self.client.post(
            self.url,
            {"title": "x" * 256, "content": "content"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_unauthenticated_user_cannot_list_notes(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_create_notes(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_by_title(self):
        Note.objects.create(title="Django tips", content="Some content", creator=self.user)
        Note.objects.create(title="Python basics", content="Some content", creator=self.user)
        response = self.client.get(self.url, {"search": "Django"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Django tips")

    def test_search_by_content(self):
        Note.objects.create(title="Note 1", content="About Django REST", creator=self.user)
        Note.objects.create(title="Note 2", content="About Python", creator=self.user)
        response = self.client.get(self.url, {"search": "REST"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Note 1")

    def test_search_no_match(self):
        Note.objects.create(title="Django tips", content="Some content", creator=self.user)
        response = self.client.get(self.url, {"search": "nonexistent"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_ordering_by_created_at_ascending(self):
        note1 = Note.objects.create(title="First", content="Content", creator=self.user)
        note2 = Note.objects.create(title="Second", content="Content", creator=self.user)
        response = self.client.get(self.url, {"ordering": "created_at"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(results[0]["id"], note1.pk)
        self.assertEqual(results[1]["id"], note2.pk)

    def test_ordering_by_created_at_descending(self):
        note1 = Note.objects.create(title="First", content="Content", creator=self.user)
        note2 = Note.objects.create(title="Second", content="Content", creator=self.user)
        response = self.client.get(self.url, {"ordering": "-created_at"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(results[0]["id"], note2.pk)
        self.assertEqual(results[1]["id"], note1.pk)


class NoteRetrieveUpdateDeleteTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="<PASSWORD>")
        self.client.force_authenticate(user=self.user)
        self.note = Note.objects.create(title="Existing Note", content="Existing content", creator=self.user)
        self.url = reverse("note-detail", kwargs={"version": "v1", "pk": self.note.pk})

    def test_retrieve_note_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.note.pk)
        self.assertEqual(response.data["title"], "Existing Note")
        self.assertEqual(response.data["content"], "Existing content")

    def test_retrieve_note_not_found(self):
        url = reverse("note-detail", kwargs={"version": "v1", "pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_title(self):
        response = self.client.patch(self.url, {"title": "Updated Title"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Title")
        self.assertEqual(response.data["content"], "Existing content")

    def test_partial_update_content(self):
        response = self.client.patch(self.url, {"content": "New content"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "New content")

    def test_partial_update_not_found(self):
        url = reverse("note-detail", kwargs={"version": "v1", "pk": 9999})
        response = self.client.patch(url, {"title": "X"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_title_too_long(self):
        response = self.client.patch(self.url, {"title": "x" * 256}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_note_success(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_delete_note_not_found(self):
        url = reverse("note-detail", kwargs={"version": "v1", "pk": 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_not_allowed(self):
        response = self.client.put(self.url, {"title": "X", "content": "Y"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_not_allowed_if_not_creator(self):
        other_user = User.objects.create_user(username="otheruser", password="<PASSWORD>")
        self.client.force_authenticate(user=other_user)
        response = self.client.patch(self.url, {"content": "Y"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_not_allowed_if_not_creator(self):
        other_user = User.objects.create_user(username="otheruser", password="<PASSWORD>")
        self.client.force_authenticate(user=other_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_v1_response_has_creator_field(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("creator", response.data)
        self.assertNotIn("owner", response.data)

    def test_v2_response_has_owner_field(self):
        url = reverse("note-detail", kwargs={"version": "v2", "pk": self.note.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("owner", response.data)
        self.assertNotIn("creator", response.data)

    def test_v2_owner_matches_creator(self):
        url = reverse("note-detail", kwargs={"version": "v2", "pk": self.note.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["owner"], self.user.pk)


@override_settings(CACHES=LOCMEM_CACHE)
class NotesCacheTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cacheuser", password="testpass")
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse("note-list", kwargs={"version": "v1"})
        self.cache_key = f"notes_list_{self.user.id}"
        cache.clear()

    def test_list_populates_cache(self):
        Note.objects.create(title="Note", content="Content", creator=self.user)
        self.assertIsNone(cache.get(self.cache_key))
        self.client.get(self.list_url)
        self.assertIsNotNone(cache.get(self.cache_key))

    def test_create_invalidates_cache(self):
        self.client.get(self.list_url)
        self.assertIsNotNone(cache.get(self.cache_key))
        self.client.post(self.list_url, {"title": "New", "content": "Content"}, format="json")
        self.assertIsNone(cache.get(self.cache_key))

    def test_update_invalidates_cache(self):
        note = Note.objects.create(title="Note", content="Content", creator=self.user)
        self.client.get(self.list_url)
        self.assertIsNotNone(cache.get(self.cache_key))
        url = reverse("note-detail", kwargs={"version": "v1", "pk": note.pk})
        self.client.patch(url, {"title": "Updated"}, format="json")
        self.assertIsNone(cache.get(self.cache_key))

    def test_delete_invalidates_cache(self):
        note = Note.objects.create(title="Note", content="Content", creator=self.user)
        self.client.get(self.list_url)
        self.assertIsNotNone(cache.get(self.cache_key))
        url = reverse("note-detail", kwargs={"version": "v1", "pk": note.pk})
        self.client.delete(url)
        self.assertIsNone(cache.get(self.cache_key))
