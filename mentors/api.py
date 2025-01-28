from django.shortcuts import aget_object_or_404
from ninja_extra import NinjaExtraAPI, api_controller, http_get, http_post, permissions

from mentors.models import Mentor
from mentors.schemas import MentorDetailSchema, MentorSchema
from users.models import UserProfile

api = NinjaExtraAPI()


@api_controller("/mentors", tags=["Mentors"], permissions=[permissions.IsAuthenticatedOrReadOnly])
class AsyncMentorController:
    @http_get("/", response=list[MentorSchema])
    async def list_mentors(self, is_active: bool | None = None):
        """
        List mentors with optional filters for `is_active`.
        """
        mentors = Mentor.objects.all()
        if is_active is not None:
            mentors = mentors.filter(is_active=is_active)

        return mentors

    @http_get("/{mentor_slug}", response=MentorDetailSchema)
    async def get_mentor(self, mentor_slug: str):
        """
        Retrieve details of a single mentor by slug field.
        """
        return await aget_object_or_404(Mentor, slug=mentor_slug)

    @http_post("/{mentor_slug}", response=MentorDetailSchema)
    async def pick_mentor(self, request, mentor_slug: str):
        """
        Pick preferred mentor by slug field.
        """
        mentor = await aget_object_or_404(Mentor, slug=mentor_slug)
        user_profile = await aget_object_or_404(UserProfile, user=request.user)
        user_profile.preferred_mentor = mentor
        await user_profile.asave()
        return mentor
