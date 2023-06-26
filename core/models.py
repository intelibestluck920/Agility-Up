from django.db import models
from django.db.models import Avg
from accounts.models import User
from statistics import mean
from django.utils.text import slugify
from datetime import datetime
from .choices import TAG_CHOICES


# Create your models here.


class Team(models.Model):
    name = models.CharField(max_length=512)
    slug = models.SlugField(null=True, blank=True)

    team_lead = models.ForeignKey(User, on_delete=models.PROTECT, related_name='team_lead')
    team_members = models.ManyToManyField(User, through='TeamMembers')

    pause = models.BooleanField(default=False)

    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Team, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}-{self.id}'

    def get_team_sentiment(self):
        feedbacks = FeedBack.objects.filter(Team_id=self.id)
        if feedbacks:
            score_arr = []
            for feed in feedbacks:
                score_arr.append(feed.score)

            if len(score_arr) > 1:
                score = mean(score_arr)
            elif len(score_arr) == 1:
                score = score_arr[0]

            score = round(score, 1)
            return score
        else:
            return 0

    def get_team_history(self):
        history = FeedBack.objects.filter(Team_id=self.id)
        history_list = []
        for his in history:
            dict = {
                "score": his.score,
                "created_at": his.created_at.date().strftime("%b %d %Y"),
                "month": his.month,
                "sprint": his.Sprint.name,
                "sprint_start_date": his.Sprint.start_date.strftime("%b %d %Y"),
            }
            history_list.append(dict)

        return history_list

    def get_team_current_score(self):
        feedback = FeedBack.objects.filter(Team_id=self.id, addressed=False).values('score')
        if feedback and feedback.count() > 1:
            score = feedback.aggregate(Avg('score'))
            score = round(score['score__avg'], 1)

            if score > 0:
                dict = {
                    'sentiment': 'up',
                    'score': score,
                }
                return dict
            elif score < 0:
                dict = {
                    'sentiment': 'down',
                    'score': score,
                }
                return dict
            elif score == 0:
                dict = {
                    'sentiment': 'stable',
                    'score': score,
                }
                return dict
        elif feedback.count() == 1:
            dict = {
                'sentiment': 'stable',
                'score': feedback[0]['score'],
            }
            return dict
        else:
            dict = {
                'sentiment': 'stable',
                'score': 0.0,
            }
            return dict
        # for feed in feedback:
        #     print(feed.score, feed.created_at)
        # return FeedBack.objects.filter(Team_id=self.id).values('score', 'created_at')

    def get_current_sprint(self):
        date = datetime.today()
        sprint = Sprint.objects.filter(Team=self, start_date__lte=date, end_date__gte=date)
        if sprint.count() > 0:
            return sprint[0].id
        else:
            id = ''
            return id


class TeamMembers(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    create_at = models.DateTimeField(auto_now_add=True)     # TODO fix create_at
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'M:{self.member} / T:{self.team}'


class Sprint(models.Model):
    name = models.CharField(max_length=9)
    Team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)

    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f'{self.name} / T:{self.Team}'

    def feedback_elevate(self):
        Feedback_list = FeedBack.objects.filter(Sprint=self, addressed=False, score__lte=-0.25).values('id')
        return Feedback_list


class FeedBack(models.Model):
    Team = models.ForeignKey(Team, on_delete=models.CASCADE)
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Sprint = models.ForeignKey(Sprint, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='Sprint')

    feedback = models.TextField()
    score = models.FloatField(null=True)

    addressed = models.BooleanField(default=False)
    response = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    month = models.CharField(max_length=10, default='January')

    def __str__(self):
        return f'T:{self.Team} / U:{self.User} / S:{self.Sprint}'

    def aggregate_score(self):
        query_set = SentimentAnalysis.objects.filter(FeedBack=self, addressed=False)
        score_arr = []
        for query in query_set:
            score_arr.append(query.score)

        if len(score_arr) > 1:
            self.score = mean(score_arr)
        elif len(score_arr) == 1:
            self.score = score_arr[0]

        return self.score

    def get_tag_feedback(self, tag):
        query_set = SentimentAnalysis.objects.filter(FeedBack=self, Tag=tag)
        return query_set

    def get_feedback(self):
        query_set = SentimentAnalysis.objects.filter(FeedBack=self)
        return query_set

    def get_all_feedback(self):
        query_set = SentimentAnalysis.objects.filter(FeedBack=self)
        return query_set

    def has_negative_sentiment(self):
        negative_sent = SentimentAnalysis.objects.filter(FeedBack=self, Tag__exact='Negative', addressed=False).exists()
        return negative_sent


# class invited_user(models.Model):
#     team = models.ForeignKey(Team, on_delete=models.CASCADE)
#     email = models.EmailField()
#
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


# class UserInvites(models.Model):
#     team = models.ForeignKey(Team, on_delete=models.CASCADE)
#     email = models.EmailField()
#
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


class SentimentAnalysis(models.Model):
    FeedBack = models.ForeignKey(FeedBack, on_delete=models.CASCADE)
    User = models.ForeignKey(User, on_delete=models.CASCADE, default=2)

    feedback_sentence = models.TextField()
    score = models.FloatField()

    addressed = models.BooleanField(default=False)
    Tag = models.CharField(max_length=10, default='Neutral')

    response = models.TextField(default=' ')

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'F:{self.FeedBack} / {self.Tag} / {self.addressed}'

# class SentimentAnalysis(models.Model):
#     FeedBack = models.ForeignKey(FeedBack, on_delete=models.CASCADE)
#
#     feedback_sentence = models.TextField()
#     score = models.FloatField()
#
#     addressed = models.BooleanField(default=False)
#     Tag = models.CharField(max_length=10, default='Neutral')
#
#     response = models.TextField(default=' ')
#
#     def __str__(self):
#         return f'F:{self.FeedBack} / {self.Tag} / {self.addressed}'


class FeedbackElevationRecord(models.Model):
    OriginalSprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, related_name='OriginalSprint')
    CurrentSprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, related_name='CurrentSprint')

    Feedback = models.ForeignKey(FeedBack, on_delete=models.CASCADE, related_name='Feedback')

    def __str__(self):
        return f'{self.OriginalSprint} / {self.CurrentSprint} / {self.Feedback}'


class Bucket(models.Model):
    Sentiment = models.ManyToManyField(SentimentAnalysis)
    FeedBack = models.ManyToManyField(FeedBack)
    Team = models.ManyToManyField(Team)

    keyword = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    Tag = models.CharField(max_length=10, default='Neutral')
