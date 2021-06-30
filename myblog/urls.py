from django.urls import path, include

from . import views

app_name = "blog"
urlpatterns = [
    path("top/", include([
        path("", views.top, name="top"),
        path("update/<int:pk>/", views.ProfileUpdate.as_view(), name="profile-update"),
    ])),
    path("post/", include([
            path("list/", views.PostListView.as_view(), name="post-list"),
            path("detail/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),
            path("create/", views.PostCreateView.as_view(), name="post-create"),
            path("update/<int:pk>/", views.PostUpdateView.as_view(), name="post-update"),
            path("delete/<int:pk>/", views.PostDeleteView.as_view(), name="post-delete"),
    ])),
]
