from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from django.utils.translation import gettext_lazy as _
from django.db import models
from content.models import Post


class ProfileSearchFilter(SearchFilter):
    search_title = _(
        "Search by username, first_name &/or last_name, or any elements of birth_date"
    )
    search_description = _(
        "Enter please any string  or birth_date (ex. 01-26) to search"
    )


class PostFilter(filters.FilterSet):
    owner = filters.NumberFilter(
        field_name="owner__id", label="Filter post by owner ID"
    )
    liked_by_me = filters.BooleanFilter(
        method="filter_liked_by_me", label="Posts Liked by me"
    )
    search = filters.CharFilter(
        method="filter_search", label=_("Search by hashtags, title & content")
    )

    class Meta:
        model = Post
        fields = [
            "owner",
            "liked_by_me",
        ]

    def filter_liked_by_me(self, queryset, name, value):
        if value:
            return queryset.filter(
                likes__owner=self.request.user.profile, likes__is_liked=True
            )
        else:
            return queryset.filter(
                likes__owner=self.request.user.profile, likes__is_unliked=True
            )

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(hashtags__icontains=value)
            | models.Q(title__icontains=value)
            | models.Q(content__icontains=value)
        )
