from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404, HttpResponseRedirect
from django.http.response import HttpResponse, HttpResponseNotAllowed
from django.views import generic
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.db.models import Count, Prefetch
from django.urls import reverse_lazy, reverse
from braces.views import SelectRelatedMixin

from teams.models import Team
from .models import Publication, Comment, PollOption, Vote
from .forms import PollOptionForm, PublicationForm, ReplyForm, CommentForm

User = get_user_model()

class CreatePost(LoginRequiredMixin, SelectRelatedMixin, UserPassesTestMixin, generic.CreateView):
  form_class = PublicationForm
  template_name = 'message_board/post_form.html'

  def get_success_url(self):
    return reverse_lazy("teams:message_board:post_detail", kwargs={"slug": self.object.team.slug,
                                                                   "pk": self.object.pk})

  def form_valid(self, form):
    self.object = form.save(commit=False)
    self.object.author = self.request.user
    self.object.team = Team.objects.get(slug=self.kwargs.get('slug'))
    self.object.save()
    return super().form_valid(form)

  def get_context_data(self, **kwargs):
    context = super(CreatePost, self).get_context_data(**kwargs)
    context["current_team"] = self.kwargs.get('slug')
    return context

  def test_func(self):
    current_team = self.kwargs.get('slug')
    return self.request.user.teams.filter(slug=current_team).exists()


class UpdatePost(LoginRequiredMixin, SelectRelatedMixin, UserPassesTestMixin, generic.UpdateView):
  template_name = 'message_board/update_post_form.html'
  model = Publication
  form_class = PublicationForm
  select_related = ('author', 'team')

  def get_success_url(self):
    return reverse_lazy("teams:message_board:post_detail", kwargs={"slug": self.object.team.slug,
                                                                   "pk": self.object.pk})

  def test_func(self):
    return self.request.user.username == self.get_object().author.username

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["current_team"] = self.kwargs.get('slug')
    return context


class DeletePost(LoginRequiredMixin, SelectRelatedMixin, UserPassesTestMixin, generic.DeleteView):
  model = Publication
  select_related = ('author', 'team')
  template_name = 'message_board/post_confirm_delete.html'

  def get_success_url(self):
    return reverse_lazy('teams:message_board:team_posts', kwargs={'slug': self.kwargs.get('slug')})

  def delete(self, *args, **kwargs):
    messages.success(self.request, 'Post Deleted')
    return super().delete(*args, **kwargs)

  def test_func(self):
    return self.request.user.username == self.get_object().author.username

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    return context


class PostDetail(LoginRequiredMixin, UserPassesTestMixin, SelectRelatedMixin, generic.DetailView):
  model = Publication
  select_related = ('author', 'team')
  template_name = 'message_board/post_detail.html'

  def get_queryset(self):
    self.post_detail = Publication.objects.filter(id=self.kwargs.get("pk"))
    return self.post_detail.all()

  def test_func(self):
    current_team = self.kwargs.get('slug')
    return self.request.user.teams.filter(slug=current_team).exists()

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["form"] = CommentForm
    context["current_team"] = self.kwargs.get("slug")
    return context


class PostList(LoginRequiredMixin, UserPassesTestMixin, SelectRelatedMixin, generic.ListView):
  model = Publication
  select_related = ('author', 'team')
  context_object_name = 'posts_list'
  template_name = 'message_board/message_board.html'

  def get_queryset(self):
    try:
      if(self.kwargs.get("drafts") == "drafts"):
        self.post_team = Publication.objects.select_related(
            'team').filter(team__slug=self.kwargs.get("slug"), author=self.request.user, is_active=False)
      else:
        self.post_team = Publication.objects.select_related(
            'team').filter(team__slug=self.kwargs.get("slug"), is_active=True)
    except Team.DoesNotExist:
      raise Http404
    else:
      return self.post_team.all()

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["current_team"] = self.kwargs.get('slug')
    context["team_obj"] = Team.objects.get(slug=self.kwargs.get('slug'))
    
    if(self.kwargs.get("drafts") == "drafts"): context["post_type"] = "Drafts"
    else: context["post_type"] = "Posts"
    #context["posts_by_user"] = Publication.objects.select_related('author').filter(author=self.request.user)
    return context

  def test_func(self):
    current_team = self.kwargs.get('slug')
    return self.request.user.teams.filter(slug=current_team).exists()


class UserPostList(LoginRequiredMixin, generic.ListView):
  model = Publication
  context_object_name = 'posts_list'
  template_name = 'message_board/partials/post_list.html'

  def get_queryset(self):
    try:
      self.post_user = Publication.objects.select_related(
          'author').filter(author__username=self.kwargs.get("username"))
    except User.DoesNotExist:
      raise Http404
    else:
      return self.post_user.all()

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["usuario"] = self.kwargs.get("username")
    return context


class CreateCommentView(LoginRequiredMixin, UserPassesTestMixin, SelectRelatedMixin, generic.CreateView):
  model = Comment
  form_class = CommentForm
  template_name = 'message_board/partials/comment_form.html'

  def form_valid(self, form):
    self.object = form.save(commit=False)
    self.object.author = self.request.user
    self.object.post = Publication.objects.get(id=self.kwargs.get('pk'))
    return super().form_valid(form)

  def test_func(self):
    current_team = self.kwargs.get('slug')
    return self.request.user.teams.filter(slug=current_team).exists()

  def get_success_url(self):
    return reverse("teams:message_board:post_detail", kwargs={"slug": self.kwargs.get('slug'), "pk": self.object.post.id})
  

class CreateReplyToCommentView(LoginRequiredMixin, UserPassesTestMixin, SelectRelatedMixin, generic.CreateView):
  model = Comment
  form_class = ReplyForm
  template_name = 'message_board/partials/reply_form.html'

  def form_valid(self, form):
    self.object = form.save(commit=False)
    self.object.author = self.request.user
    self.object.post = Publication.objects.get(id=self.kwargs.get('pk'))
    self.object.parent = Comment.objects.get(id = self.kwargs.get("parent_pk"))
    self.object.save()
    return super().form_valid(form)

  def test_func(self):
    current_team = self.kwargs.get('slug')
    return self.request.user.teams.filter(slug=current_team).exists()
  
  def get_success_url(self):
    return reverse("teams:message_board:comment_detail", kwargs={"slug": self.kwargs.get('slug'), "pk": self.object.id})
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['pub_slug'] = self.kwargs.get('slug')
    context['pub_pk'] = self.kwargs.get('pk')
    context['comment_pk'] = self.kwargs.get("parent_pk")
    return context

class CommentListView(LoginRequiredMixin, generic.ListView):
  model = Comment
  template_name = 'message_board/partials/comment_list2.html'
  context_object_name = 'comments_list'

  def get_queryset(self):
    parent_pk = int(self.kwargs.get("parent_pk"))
    if parent_pk < 0:
      parent=None
    else:
      parent = self.kwargs.get("parent_pk")
    try:
      # self.comments = Comment.objects.all().filter(post__id=self.kwargs.get("pk"), parent=None).prefetch_related(
      #     Prefetch('childs', Comment.objects.annotate(Count('childs')))).annotate(Count('childs'))
      self.comments = Comment.objects.all().filter(post__id=self.kwargs.get("pk"),
                                                   parent=parent).annotate(Count('childs')).order_by('-creation_date')
    except Publication.DoesNotExist:
      raise Http404
    else:
      return self.comments.all()

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["team_slug"] = self.kwargs.get("slug")
    context["pub_pk"] = self.kwargs.get("pk")
    context["form"] = ReplyForm
    return context


class CommentDetailView(LoginRequiredMixin, generic.DetailView):
  model = Comment
  template_name = 'message_board/partials/comment_detail.html'
  context_object_name = 'comment'
  
  def  get_queryset(self):
      return Comment.objects.all().filter(id = self.kwargs.get("pk")).annotate(Count('childs'))
  


class PollOptionCreateView(LoginRequiredMixin, SelectRelatedMixin, UserPassesTestMixin, generic.CreateView):
  form_class = PollOptionForm
  select_related = ('publication',)
  template_name = 'message_board/partials/poll_option_form.html'
  context_object_name = 'option'

  def form_valid(self, form):
    publication = Publication.objects.get(id=self.kwargs.get("pk"))
    self.object = form.save(commit=False)
    self.object.publication = publication
    self.object.save()
    return super().form_valid(form)

  def get_success_url(self):
    kwargs = {'slug': self.kwargs.get("slug"),
              'pub_pk': self.kwargs.get("pk"),
              'pk': self.object.id}
    return reverse_lazy("teams:message_board:poll_option_detail", kwargs=kwargs)

  def get_context_data(self, **kwargs):
    context = super(PollOptionCreateView, self).get_context_data(**kwargs)
    context["publication_id"] = self.kwargs.get("pk")
    context["current_team"] = self.kwargs.get("slug")
    return context

  def test_func(self):
    return self.request.user == get_object_or_404(Publication, id=self.kwargs.get("pk")).author


class PollOptionDetailView(LoginRequiredMixin, generic.DetailView):
  model = PollOption
  # select_related = ('publication', 'team')
  template_name = 'message_board/partials/option_detail.html'
  context_object_name = 'option'


class PollOptionListView(LoginRequiredMixin, SelectRelatedMixin, generic.ListView):
  model = PollOption
  select_related = ('publication')
  template_name = 'message_board/partials/poll_option_list.html'
  context_object_name = 'poll_option_list'

  def get_queryset(self):
    try:
      self.list = PollOption.objects.select_related(
          'publication').filter(publication_id=self.kwargs.get('pub_pk'))
    except Publication.DoesNotExist:
      raise Http404
    else:
      return self.list.all()
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["total_votes"] = Vote.objects.filter(publication_id = self.kwargs.get('pub_pk')).count()
      return context
  


class PollOptionUpdateView(LoginRequiredMixin, generic.UpdateView):
  model = PollOption
  form_class = PollOptionForm
  template_name = 'message_board/partials/update_poll_option_form.html'

  def form_valid(self, form):
    self.object = form.save()
    print('aver:', self.object)
    return render(self.request,
                  'message_board/partials/option_detail.html',
                  context={"option": self.object, })

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["current_team"] = self.kwargs.get("slug")
    context["publication_id"] = self.kwargs.get("pub_pk")
    context["option"] = self.object
    return context


class PollOptionDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
  model = PollOption

  def delete(self, *args, **kwargs):
    self.object = self.get_object()
    self.object.delete()
    return HttpResponse("<p>Option Deleted</p>")

  def test_func(self):
    return self.request.user == get_object_or_404(Publication, id=self.kwargs.get("pub_pk")).author


def vote(request, slug, pub_pk, pk, action):
  if request.method == 'POST':
    user = request.user
    # vote
    if action == 'vote':
      user_vote_exists = Vote.objects.filter(
          user=user, publication_id=pub_pk).exists()
      with transaction.atomic():
        # removes old vote if exists
        if user_vote_exists:
          old_option = get_object_or_404(
              PollOption, publication_id=pub_pk, voters=user)
          old_option.votes -= 1
          old_option.voters.remove(user)
          old_option.save()
        # vote is added/updated
        option = get_object_or_404(PollOption, id=pk)
        option.votes += 1
        option.voters.add(user, through_defaults={
                          'publication': option.publication})
        option.save()

    # unvote
    elif action == "unvote":
      user_vote_exists = Vote.objects.filter(user=user,
                                             publication_id=pub_pk,
                                             poll_option_id=pk).exists()
      if user_vote_exists:
        option = get_object_or_404(PollOption, id=pk)
        with transaction.atomic():
          option.votes -= 1
          option.voters.remove(user)
          option.save()

    return redirect(reverse('teams:message_board:poll_option_list', kwargs={'slug': slug,
                                                                            'pub_pk': pub_pk}))
