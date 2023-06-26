from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SentimentAnalysis, FeedBack, Bucket
from .model import generate_intent, check_similarity
from .helpers import sentence_splitter, sentiment_analysis, capitalize, tag_return
import datetime


@receiver(post_save, sender=SentimentAnalysis)
def update_score(sender, instance, created, **kwargs):
    if not created:
        score = instance.FeedBack.aggregate_score()
        instance.FeedBack.score = score
        instance.save()
    elif created:
        topic_list = generate_intent(instance.feedback_sentence)
        topics = list(Bucket.objects.all().values_list('keyword', flat=True))
        response = check_similarity(topic_list, topics)

        if response['new']:
            obj = Bucket.objects.create(
                keyword=response['topics'], Tag=instance.Tag
            )
            obj.Sentiment.add(instance)
            obj.FeedBack.add(instance.FeedBack)
            obj.Team.add(instance.FeedBack.Team)
        elif not response['new']:
            obj = Bucket.objects.get(keyword=response['topics'])
            obj.Sentiment.add(instance)
            obj.FeedBack.add(instance.FeedBack)
            obj.Team.add(instance.FeedBack.Team)
            obj.save()


@receiver(post_save, sender=FeedBack)  # TODO evaluate pre_save instead of current
def add_month_name(sender, instance, created, **kwargs):
    if created:
        print('created, signal called')
        # feedback_arr = sentence_splitter(instance.feedback)
        # for x in range(len(feedback_arr)):
        #     score = sentiment_analysis(feedback_arr[x])
        #     score = round(score, 1)
        #     feedback = capitalize(feedback_arr[x])
        #     Tag = tag_return(score)
        #     SentimentAnalysis.objects.create(FeedBack=instance,
        #                                      feedback_sentence=feedback,
        #                                      score=score,
        #                                      Tag=Tag, User=instance.User)
        #
        # score = instance.aggregate_score()
        # instance.score = round(score, 1)
        # instance.month = instance.created_at.date().strftime('%B')
        # instance.save()
        # if instance.score is None:
        #     instance.score = 0.0
        #     instance.save()

        print('created, signal ended')
        # TODO check/handle if score is none
