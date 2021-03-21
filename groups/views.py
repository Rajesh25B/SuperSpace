# Django imports
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db import IntegrityError

# Login imports
from . import models
from .models import Group, GroupMember
# Create your views here.


class CreateGroup(LoginRequiredMixin, generic.CreateView):
    ''' Create a new group '''
    fields = ('name', 'description')
    model = Group


class SingleGroup(generic.DetailView):
    ''' View a single requested group '''
    model = Group


class ListGroups(generic.ListView):
    ''' Lists all groups '''
    model = Group


class JoinGroup(LoginRequiredMixin, generic.RedirectView):
    ''' Joining a group '''

    def get_redirect_url(self, *args, **kwargs):
        return reverse("groups:single", kwargs={"slug": self.kwargs.get("slug")})

    def get(self, request, *args, **kwargs):
        group = get_object_or_404(Group, slug=self.kwargs.get("slug"))

        try:
            GroupMember.objects.create(user=self.request.user, group=group)

        except IntegrityError:
            messages.warning(
                self.request, ("Warning, already a member of {}".format(group.name)))

        else:
            messages.success(
                self.request, "You are now a member of the {} group.".format(group.name))

        return super().get(request, *args, **kwargs)


class LeaveGroup(LoginRequiredMixin, generic.RedirectView):
    ''' Leave the group'''

    def get_redirect_url(self, *args, **kwargs):
        return reverse("groups:single", kwargs={"slug": self.kwargs.get("slug")})

    def get(self, request, *args, **kwargs):

        try:

            membership = models.GroupMember.objects.filter(
                user=self.request.user,
                group__slug=self.kwargs.get("slug")
            ).get()

        except models.GroupMember.DoesNotExist:
            messages.warning(
                self.request,
                "You can't leave this group because you aren't in it."
            )
        else:
            membership.delete()
            messages.success(
                self.request,
                "You have successfully left this group."
            )
        return super().get(request, *args, **kwargs)
