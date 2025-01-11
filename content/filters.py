from rest_framework.filters import SearchFilter
from django.utils.translation import gettext_lazy as _


class CustomSearchFilter(SearchFilter):
    search_title = _(
        "Search by nickname, first_name &/or last_name, or any elements of birth_date"
    )
    search_description = _(
        "Enter please any string  or birth_date (ex. 01-26) to search"
    )
