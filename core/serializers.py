from rest_framework import serializers
from .models import *
from accounts.serializers import UserInfominimal


class TeamFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBack
        fields = ('score', 'created_at',)


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name',)


class TeamUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name', 'pause')


class InviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    team_id = serializers.IntegerField()


class InviteLinkSerializer(serializers.Serializer):
    url = serializers.URLField()


class SprintSerializer(serializers.Serializer):
    cadence = serializers.CharField(max_length=128)
    start_date = serializers.DateField(input_formats=['%m/%d/%Y'])
    team = serializers.IntegerField()

    # def create(self, validated_data):
    #     return Comment(**validated_data)


class SprintDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = ('id',)


class SprintInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = ('id', 'name', 'start_date', 'end_date')


class FeedBackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBack
        fields = ('Sprint', 'feedback')


class AddressFeedBack(serializers.ModelSerializer):
    class Meta:
        model = SentimentAnalysis
        fields = ('response',)


class FeedbackAnalysis(serializers.ModelSerializer):
    User = UserInfominimal(read_only=True, many=False)
    # created_at = serializers.DateTimeField(format='%b%D%Y')
    class Meta:
        model = SentimentAnalysis
        # exclude = ('FeedBack',)
        fields = ('User', 'feedback_sentence', 'score', 'addressed', 'Tag', 'response', 'created_at')


# class FeedbackAnalysis(serializers.ModelSerializer):
#     class Meta:
#         model = SentimentAnalysis
#         exclude = ('FeedBack',)

class TeamMembersSerializer(serializers.ModelSerializer):
    team = serializers.StringRelatedField()
    member = serializers.StringRelatedField()

    class Meta:
        model = TeamMembers
        exclude = ('created_at', 'updated_at',)


class TeamFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBack
        fields = ('score', 'created_at',)


class BucketSerializer(serializers.ModelSerializer):
    Sentiment = FeedbackAnalysis(read_only=True, many=True)
    FeedBack = FeedBackSerializer(read_only=True, many=True)
    Team = TeamSerializer(read_only=True, many=True)

    class Meta:
        model = Bucket
        fields = ('Sentiment', 'FeedBack', 'Team', 'keyword')