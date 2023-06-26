from django.shortcuts import redirect
from django.db.models import Q, Prefetch, Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .response import ResponseThen
from rest_framework import status
from django.core.mail import send_mail

from .models import *
from accounts.models import User
from .serializers import *

from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, timezone

from .helpers import sentiment_analysis, sentence_splitter, capitalize, tag_return, average
from invites.models import Invite
from product.models import ProductAreaTeams, ProductTeams, EnterpriseProducts, Product, ProductArea, Enterprise

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from permissions.permissions import IsTeam
from permissions.models import assigned_permissions
from .model import generate_summary, gpt3_data_analysis, generate_negative_experiences
from functools import reduce


# Create your views here.


class teamlist(APIView):
    permission_classes = (IsAuthenticated, IsTeam)

    def get(self, request):
        date = datetime.today()
        teams_id = TeamMembers.objects.filter(member=request.user).values_list('team')
        invites = Invite.objects.filter(invitee=request.user.email, accepted=False).values('Team')
        teams_invite = Team.objects.filter(id__in=invites).values('id', 'name')

        if teams_id.count() > 0:
            teams = Team.objects.filter(id__in=teams_id)
            list = []
            # accumulative_history = []
            # feed = FeedBack.objects.filter(Team_id__in=teams_id)
            # for f in feed:
            #     acc_dict = {
            #         "score": f.score,
            #         "created_at": f.created_at.date().strftime("%b %d %Y"),
            #         "month": f.month,
            #         "sprint": f.Sprint.name,
            #         "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
            #     }
            #     accumulative_history.append(acc_dict)
            for team in teams:
                try:
                    if Sprint.objects.filter(Team=team, start_date__lte=date, end_date__gte=date).count() > 0:
                        current_sprint_exists = True
                    else:
                        current_sprint_exists = False
                except Sprint.DoesNotExist:
                    current_sprint_exists = False

                dict = {}
                dict = {
                    'id': team.id,
                    'name': team.name,
                    'score': team.get_team_sentiment(),
                    'history': get_history_func(type='team_id', type_id=team.id),
                    'team_paused': team.pause,
                    'current_sprint_exists': current_sprint_exists,
                    'current_sprint_id': team.get_current_sprint(),
                }
                list.append(dict)

            context = {
                'data': list,
                'invited_to_teams': teams_invite,
                'accumulative_history': get_history_func(type='user-teams', type_id=request.user.id),
            }
        else:
            context = {
                'invited_to_teams': teams_invite,
                'accumulative_history': get_history_func(type='user-teams', type_id=request.user.id),
            }

        # serializer = TeamSerializer(teams, many=True)
        return Response(context)


class teamdetail(APIView):
    permission_classes = (IsAuthenticated, IsTeam)

    def get(self, request, pk):
        team = Team.objects.get(id=pk)
        date = datetime.today()
        qs = Sprint.objects.filter(Team_id=pk)
        team_score = team.get_team_sentiment()
        team_history = team.get_team_history()
        current_sentiment = team.get_team_current_score()
        if qs.exists():
            sprints = Sprint.objects.filter(Team_id=pk).values('id', 'name', 'start_date', 'end_date')
            try:
                sp = Sprint.objects.get(Team_id=team.id, start_date__lte=date, end_date__gte=date)
                sprint = sp.id
                sprint_exists = 'true'
            except Sprint.DoesNotExist:
                sprint = ''
                sprint_exists = 'false'
        else:
            sprints = ''
            sprint = ''
            sprint_exists = 'false'
        total_members = TeamMembers.objects.filter(team_id=pk).count()
        members = TeamMembers.objects.filter(team_id=pk).values('member')
        id_list = []
        for member in members:
            id_list.append(member['member'])
        members_data = User.objects.filter(id__in=id_list).values('id', 'email')
        dict = {
            'team_id': team.id,
            'team_name': team.name,
            'team_score': team_score,
            'team_history': get_history_func(type='team_id', type_id=team.id),
            'sprints': sprints,
            'current_sprint': sprint,
            'total_members': total_members,
            'members': members_data,
            'current_sprint_exists': sprint_exists,
            'team_paused': team.pause,
            'current_sentiment': current_sentiment,
        }
        # serializer = TeamSerializer(team, many=False)
        return Response(dict)


class createteam(APIView):
    permission_classes = (IsAuthenticated, IsTeam)

    def post(self, request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            member = serializer.save(team_lead=request.user)
            TeamMembers.objects.create(team_id=member.id, member=request.user)
        return Response(serializer.data)


class teamupdate(APIView):
    permission_classes = (IsAuthenticated, IsTeam)

    def post(self, request, pk):
        team = Team.objects.get(id=pk)
        serializer = TeamUpdateSerializer(instance=team, data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data)

    def get(self, request, pk):
        team = Team.objects.get(id=pk)
        serializer = TeamSerializer(team, many=False)
        return Response(serializer.data)


class invitemember(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = InviteSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            id = serializer.data['team_id']
            email = serializer.data['email']
            team = Team.objects.get(id=id)
            subject = f'invited to {team.name}'
            message = f'Welcome, you have been invited to AgilityUp, click the link below to join. \n \
                        http://dev.agilityup.ai/teams/join/{team.id}/{team.slug}'  # TODO change url to frontend production
            to = []
            to.append(email)
            from_email = 'agility.up.ai.test@gmail.com'
            send_mail(
                subject,
                message,
                from_email,
                to,
                fail_silently=False
            )
            Invite.objects.create(
                invitee=email, Inviter_id=request.user.id, Team_id=team.id,
            )
            assigned_permissions.objects.create(email=email, user_exists=False)

            # Invitation = get_invitation_model()
            # email = serializer.data['email']
            # invite = Invitation.create(email, inviter=request.user)
            # invite.send_invitation(request)

        return Response(serializer.data)


class inviteduser(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, slug):
        response = {
            'Detail': 'user added successfully'
        }
        if TeamMembers.objects.filter(team_id=pk, member=request.user).exists():
            response = {
                'Detail': 'user added successfully'
            }
            return Response(response)
        elif Invite.objects.filter(invitee=request.user.email, Team_id=pk, accepted=False).exists():
            invite = Invite.objects.get(invitee=request.user.email, Team_id=pk)
            team_member = TeamMembers.objects.create(team_id=pk, member=request.user)
            team_member.save()
            invite.accepted = True
            invite.save()

            return Response(response)
        else:
            return Response(response)


class createsprint(APIView):
    permission_classes = (IsAuthenticated, IsTeam)

    def post(self, request):
        serializer = SprintSerializer(data=request.data)
        check = Sprint.objects.filter(Team_id=serializer.initial_data['team'])
        if check:
            team = Team.objects.get(id=serializer.initial_data['team'])
            message = {'error': f'Sprint for {team.name} already exists'}
            return Response(message, status=status.HTTP_403_FORBIDDEN)
        else:
            if serializer.is_valid(raise_exception=True):  # todo
                start_date = serializer.data['start_date']
                start_date_d = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = start_date_d + timedelta(days=int(serializer.data['cadence']))
                Sprint.objects.create(
                    name='Sprint 1', Team_id=serializer.data['team'],
                    start_date=start_date_d, end_date=end_date
                )

                return Response(serializer.data)

    # def put(self, request):
    #     obj = Sprint.objects.get(id=request.data['id'])
    #     cadence = obj.end_date - obj.start_date
    #     serializer = SprintUpdateSerializer(obj, data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         start_date = serializer.validated_data['start_date']
    #         start_date_d = datetime.strptime(str(start_date), '%Y-%m-%d')
    #         end_date = start_date_d + timedelta(days=int(cadence.days))
    #         obj.start_date = start_date_d.date()
    #         obj.end_date = end_date.date()
    #         obj.save()
    #
    #     return Response(serializer.data)

    def delete(self, request):
        serializer = SprintDeleteSerializer(data=request.data)
        if serializer.is_valid():
            sprint = Sprint.objects.get(id=request.data['id'])
            sprint.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class feedback(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = FeedBackSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            sprint = serializer.validated_data['Sprint']
            Team = sprint.Team
            user = request.user
            obj = serializer.save(Team=Team, Sprint_id=sprint.id, User=user, )

            def do_after():
                feedback_arr = sentence_splitter(obj.feedback)
                print('do after called')
                for x in range(len(feedback_arr)):
                    score = sentiment_analysis(feedback_arr[x])
                    score = round(score, 1)
                    feedback = capitalize(feedback_arr[x])
                    Tag = tag_return(score)
                    SentimentAnalysis.objects.create(FeedBack=obj,
                                                     feedback_sentence=feedback,
                                                     score=score,
                                                     Tag=Tag, User=obj.User)

                score = obj.aggregate_score()
                obj.score = round(score, 1)
                obj.month = obj.created_at.date().strftime('%B')
                obj.save()
                if obj.score is None:
                    obj.score = 0.0
                    obj.save()
                print('do after ended')

        return ResponseThen(serializer.data, do_after, status=status.HTTP_200_OK)


class addressfeedback(APIView, ):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        sent = SentimentAnalysis.objects.get(id=pk)
        serializer = AddressFeedBack(instance=sent, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(addressed=True)

        return Response(serializer.data)

    # def get(self, request, pk):
    #     feedback = SentimentAnalysis.objects.get(id=pk)
    #     serializer = F


class get_analysis(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, tag=None):
        # feedback = FeedBack.objects.get(id=pk)
        feedback = FeedBack.objects.filter(Sprint_id=pk)
        data = SentimentAnalysis.objects.none()
        if FeedbackElevationRecord.objects.filter(OriginalSprint_id=pk).exists():
            # elevated_feedbacks =
            pass
        if request.query_params.get('tag'):
            tag = request.query_params['tag']
            for feed in feedback:
                if feed.get_tag_feedback(tag).exists():
                    data |= feed.get_tag_feedback(tag)
                else:
                    pass
        elif not tag:
            for feed in feedback:
                data |= feed.get_all_feedback()

        serializer = FeedbackAnalysis(data, many=True)

        return Response(serializer.data)


# class get_analysis(APIView):
#     permission_classes = (IsAuthenticated,)
#
#     def get(self, request, pk):
#         # feedback = FeedBack.objects.get(id=pk)
#
#         data = SentimentAnalysis.objects.none()
#         if request.query_params.get('id'):
#             id = request.query_params['id']
#             feedback = FeedBack.objects.filter(Team_id=pk, Sprint_id=id)
#             for feed in feedback:
#                 if feed.get_feedback().exists():
#                     data |= feed.get_feedback()
#                 else:
#                     pass
#         elif not request.query_params.get('id'):
#             feedback = FeedBack.objects.filter(Team_id=pk)
#             for feed in feedback:
#                 data |= feed.get_all_feedback()
#
#         serializer = FeedbackAnalysis(data, many=True)
#
#         return Response(serializer.data)


class get_team_sprints(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        sprint = Sprint.objects.filter(Team_id=pk)
        serializer = SprintInfoSerializer(sprint, many=True)
        return Response(serializer.data)


class get_current_sprint(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        date = datetime.today()
        team = Team.objects.get(id=pk)
        sprint = Sprint.objects.get(Team_id=team.id, start_date__lte=date, end_date__gte=date)
        serializer = SprintInfoSerializer(sprint)
        return Response(serializer.data)


class get_team_members(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        members = TeamMembers.objects.filter(team_id=pk).values('member')
        id_list = []
        for member in members:
            id_list.append(member['member'])
        members_data = User.objects.filter(id__in=id_list).values('id', 'email', 'first_name', 'last_name')
        members = TeamMembers.objects.filter(team_id=pk)
        serializer = TeamMembersSerializer(members, many=True)
        dict = {
            'members': members_data
        }
        return Response(dict)


class get_history(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, team_id=None):
        today = datetime.today()
        today = today.replace(tzinfo=timezone.utc)
        One_W_past = today - timedelta(days=7)
        Two_W_past = today - timedelta(days=14)
        One_M_past = today - timedelta(days=30)
        Two_M_past = today - timedelta(days=60)
        Three_M_past = today - timedelta(days=90)
        Six_M_past = today - timedelta(days=180)
        One_Y_past = today - timedelta(days=365)
        one_week_list = []
        two_week_list = []
        one_month_list = []
        two_month_list = []
        three_month_list = []
        six_month_list = []
        one_year_list = []
        all_list = []

        if request.query_params.get('team_id'):
            team_id = request.query_params.get('team_id')

            One_W = FeedBack.objects.filter(Team_id=team_id, created_at__date__gte=One_W_past.date(),
                                            created_at__date__lte=today)
            Two_W = FeedBack.objects.filter(Team_id=team_id, created_at__date__gte=Two_W_past.date(),
                                            created_at__date__lte=today)
            One_M = FeedBack.objects.filter(Team_id=team_id, created_at__date__gte=One_M_past.date(),
                                            created_at__date__lte=today)
            Two_M = FeedBack.objects.filter(Team_id=team_id, created_at__date__gte=Two_M_past.date(),
                                            created_at__date__lte=today)
            Three_M = FeedBack.objects.filter(Team_id=team_id, created_at__date__gte=Three_M_past.date(),
                                              created_at__date__lte=today)
            Six_M = FeedBack.objects.filter(Team_id=team_id, created_at__date__gte=Six_M_past.date(),
                                            created_at__date__lte=today)
            One_Y = FeedBack.objects.filter(Team_id=team_id, created_at__date__gte=One_Y_past.date(),
                                            created_at__date__lte=today)
            All = FeedBack.objects.filter(Team_id=team_id)

        elif request.query_params.get('product_area_id'):
            prod_area_id = request.query_params.get('product_area_id')
            teams_list = ProductAreaTeams.objects.filter(Product_Area=prod_area_id).values('Team')

            One_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_W_past.date(),
                                            created_at__date__lte=today)
            Two_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_W_past.date(),
                                            created_at__date__lte=today)
            One_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_M_past.date(),
                                            created_at__date__lte=today)
            Two_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_M_past.date(),
                                            created_at__date__lte=today)
            Three_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                              created_at__date__lte=today)
            Six_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                            created_at__date__lte=today)
            One_Y = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_Y_past.date(),
                                            created_at__date__lte=today)
            All = FeedBack.objects.filter(Team_id__in=teams_list)

        elif request.query_params.get('product_id'):
            prod_id = request.query_params.get('product_id')
            prod_area = ProductTeams.objects.filter(Product_id=prod_id).values('Product_Area')
            teams_list = ProductAreaTeams.objects.filter(Product_Area_id__in=prod_area).values('Team')

            One_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_W_past.date(),
                                            created_at__date__lte=today)
            Two_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_W_past.date(),
                                            created_at__date__lte=today)
            One_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_M_past.date(),
                                            created_at__date__lte=today)
            Two_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_M_past.date(),
                                            created_at__date__lte=today)
            Three_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                              created_at__date__lte=today)
            Six_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                            created_at__date__lte=today)
            One_Y = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_Y_past.date(),
                                            created_at__date__lte=today)
            All = FeedBack.objects.filter(Team_id__in=teams_list)

        elif request.query_params.get('enterprise') == 1:
            prod_id = EnterpriseProducts.objects.filter(Enterprise=request.user.Enterprise).values('Product')
            prod_area = ProductTeams.objects.filter(Product_id__in=prod_id).values('Product_Area')
            teams_list = ProductAreaTeams.objects.filter(Product_Area_id__in=prod_area).values('Team')

            One_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_W_past.date(),
                                            created_at__date__lte=today)
            Two_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_W_past.date(),
                                            created_at__date__lte=today)
            One_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_M_past.date(),
                                            created_at__date__lte=today)
            Two_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_M_past.date(),
                                            created_at__date__lte=today)
            Three_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                              created_at__date__lte=today)
            Six_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                            created_at__date__lte=today)
            One_Y = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_Y_past.date(),
                                            created_at__date__lte=today)
            All = FeedBack.objects.filter(Team_id__in=teams_list)

        elif request.query_params.get('user-products') == 1:
            pass

        else:
            teams_list = TeamMembers.objects.filter(member_id=request.user.id).values('team')
            One_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_W_past.date(),
                                            created_at__date__lte=today)
            Two_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_W_past.date(),
                                            created_at__date__lte=today)
            One_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_M_past.date(),
                                            created_at__date__lte=today)
            Two_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_M_past.date(),
                                            created_at__date__lte=today)
            Three_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                              created_at__date__lte=today)
            Six_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                            created_at__date__lte=today)
            One_Y = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_Y_past.date(),
                                            created_at__date__lte=today)
            All = FeedBack.objects.filter(Team_id__in=teams_list)

        if One_W.count() > 0:
            for f in One_W:
                One_week = {
                    "score": f.score,
                    "created_at": f.created_at.date().strftime("%b %d %Y"),
                    "month": f.month,
                    "sprint": f.Sprint.name,
                    "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
                }
                one_week_list.append(One_week)
            avg = average(one_week_list)
            one_week_list.append(avg)
        if Two_W.count() > 0:
            for f in Two_W:
                Two_Week = {
                    "score": f.score,
                    "created_at": f.created_at.date().strftime("%b %d %Y"),
                    "month": f.month,
                    "sprint": f.Sprint.name,
                    "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
                }
                two_week_list.append(Two_Week)
            avg = average(two_week_list)
            two_week_list.append(avg)
        if One_M.count() > 0:
            for f in One_M:
                One_Month = {
                    "score": f.score,
                    "created_at": f.created_at.date().strftime("%b %d %Y"),
                    "month": f.month,
                    "sprint": f.Sprint.name,
                    "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
                }
                one_month_list.append(One_Month)
            avg = average(one_month_list)
            one_month_list.append(avg)
        if Two_M.count() > 0:
            for f in Two_M:
                Two_Month = {
                    "score": f.score,
                    "created_at": f.created_at.date().strftime("%b %d %Y"),
                    "month": f.month,
                    "sprint": f.Sprint.name,
                    "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
                }
                two_month_list.append(Two_Month)
            avg = average(two_month_list)
            two_month_list.append(avg)
        if Three_M.count() > 0:
            for f in Three_M:
                Three_Month = {
                    "score": f.score,
                    "created_at": f.created_at.date().strftime("%b %d %Y"),
                    "month": f.month,
                    "sprint": f.Sprint.name,
                    "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
                }
                three_month_list.append(Three_Month)
            avg = average(three_month_list)
            three_month_list.append(avg)
        if Six_M.count() > 0:
            for f in Six_M:
                Six_Month = {
                    "score": f.score,
                    "created_at": f.created_at.date().strftime("%b %d %Y"),
                    "month": f.month,
                    "sprint": f.Sprint.name,
                    "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
                }
                six_month_list.append(Six_Month)
            avg = average(six_month_list)
            six_month_list.append(avg)

        if One_Y.count() > 0:
            for f in One_Y:
                One_Year = {
                    "score": f.score,
                    "created_at": f.created_at.date().strftime("%b %d %Y"),
                    "month": f.month,
                    "sprint": f.Sprint.name,
                    "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
                }
                one_year_list.append(One_Year)
            avg = average(one_year_list)
            one_year_list.append(avg)
        if All.count() > 0:
            for f in All:
                All = {
                    "score": f.score,
                    "created_at": f.created_at.date().strftime("%b %d %Y"),
                    "month": f.month,
                    "sprint": f.Sprint.name,
                    "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
                }
                all_list.append(All)
            avg = average(all_list)
            all_list.append(avg)

        dict = {
            '1W': one_week_list,
            '2W': two_week_list,
            '1M': one_month_list,
            '2M': two_month_list,
            '3M': three_month_list,
            '6M': six_month_list,
            '1Y': one_year_list,
            'All': all_list,
        }

        return Response(dict)


def get_history_func(type, type_id):
    today = datetime.today()
    today = today.replace(tzinfo=timezone.utc)
    One_W_past = today - timedelta(days=7)
    Two_W_past = today - timedelta(days=14)
    One_M_past = today - timedelta(days=30)
    Two_M_past = today - timedelta(days=60)
    Three_M_past = today - timedelta(days=90)
    Six_M_past = today - timedelta(days=180)
    One_Y_past = today - timedelta(days=365)
    one_week_list = []
    two_week_list = []
    one_month_list = []
    two_month_list = []
    three_month_list = []
    six_month_list = []
    one_year_list = []
    all_list = []

    if type == 'team_id':
        team_id = type_id

        One_W = FeedBack.objects.filter(Team_id=team_id, created_at__date__gte=One_W_past.date(),
                                        created_at__date__lte=today)
        Two_W = FeedBack.objects.filter(Team_id=team_id, created_at__date__gte=Two_W_past.date(),
                                        created_at__date__lte=today)
        One_M = FeedBack.objects.filter(Team_id=team_id, created_at__date__gte=One_M_past.date(),
                                        created_at__date__lte=today)
        Two_M = FeedBack.objects.filter(Team_id=team_id, created_at__date__gte=Two_M_past.date(),
                                        created_at__date__lte=today)
        Three_M = FeedBack.objects.filter(Team_id=team_id, created_at__date__gte=Three_M_past.date(),
                                          created_at__date__lte=today)
        Six_M = FeedBack.objects.filter(Team_id=team_id, created_at__date__gte=Six_M_past.date(),
                                        created_at__date__lte=today)
        One_Y = FeedBack.objects.filter(Team_id=team_id, created_at__date__gte=One_Y_past.date(),
                                        created_at__date__lte=today)
        All = FeedBack.objects.filter(Team_id=team_id)

    elif type == 'product_area_id':
        prod_area_id = type_id
        teams_list = ProductAreaTeams.objects.filter(Product_Area=prod_area_id).values('Team')

        One_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_W_past.date(),
                                        created_at__date__lte=today)
        Two_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_W_past.date(),
                                        created_at__date__lte=today)
        One_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_M_past.date(),
                                        created_at__date__lte=today)
        Two_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_M_past.date(),
                                        created_at__date__lte=today)
        Three_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                          created_at__date__lte=today)
        Six_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                        created_at__date__lte=today)
        One_Y = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_Y_past.date(),
                                        created_at__date__lte=today)
        All = FeedBack.objects.filter(Team_id__in=teams_list)

    elif type == 'product_id':
        prod_id = type_id
        prod_area = ProductTeams.objects.filter(Product_id=prod_id).values('Product_Area')
        teams_list = ProductAreaTeams.objects.filter(Product_Area_id__in=prod_area).values('Team')

        One_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_W_past.date(),
                                        created_at__date__lte=today)
        Two_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_W_past.date(),
                                        created_at__date__lte=today)
        One_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_M_past.date(),
                                        created_at__date__lte=today)
        Two_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_M_past.date(),
                                        created_at__date__lte=today)
        Three_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                          created_at__date__lte=today)
        Six_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                        created_at__date__lte=today)
        One_Y = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_Y_past.date(),
                                        created_at__date__lte=today)
        All = FeedBack.objects.filter(Team_id__in=teams_list)

    elif type == 'enterprise':
        prod_id = EnterpriseProducts.objects.filter(Enterprise=type_id).values('Product')
        prod_area = ProductTeams.objects.filter(Product_id__in=prod_id).values('Product_Area')
        teams_list = ProductAreaTeams.objects.filter(Product_Area_id__in=prod_area).values('Team')

        One_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_W_past.date(),
                                        created_at__date__lte=today)
        Two_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_W_past.date(),
                                        created_at__date__lte=today)
        One_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_M_past.date(),
                                        created_at__date__lte=today)
        Two_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_M_past.date(),
                                        created_at__date__lte=today)
        Three_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                          created_at__date__lte=today)
        Six_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                        created_at__date__lte=today)
        One_Y = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_Y_past.date(),
                                        created_at__date__lte=today)
        All = FeedBack.objects.filter(Team_id__in=teams_list)

    elif type == 'user-products':
        prods = Product.objects.filter(Q(product_lead=type_id) | Q(product_creator=type_id)).values('id')
        prod_areas = ProductTeams.objects.filter(Product_id__in=prods).values('Product_Area')
        teams_list = ProductAreaTeams.objects.filter(Product_Area_id__in=prod_areas).values('Team')

        One_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_W_past.date(),
                                        created_at__date__lte=today)
        Two_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_W_past.date(),
                                        created_at__date__lte=today)
        One_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_M_past.date(),
                                        created_at__date__lte=today)
        Two_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_M_past.date(),
                                        created_at__date__lte=today)
        Three_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                          created_at__date__lte=today)
        Six_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                        created_at__date__lte=today)
        One_Y = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_Y_past.date(),
                                        created_at__date__lte=today)
        All = FeedBack.objects.filter(Team_id__in=teams_list)

    elif type == 'user-product-area':
        prod_area = ProductArea.objects.filter(
            Q(product_area_creator_id=type_id) | Q(product_area_lead_id=type_id)).values('id')
        teams_list = ProductAreaTeams.objects.filter(Product_Area_id__in=prod_area).values('Team')
        One_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_W_past.date(),
                                        created_at__date__lte=today)
        Two_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_W_past.date(),
                                        created_at__date__lte=today)
        One_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_M_past.date(),
                                        created_at__date__lte=today)
        Two_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_M_past.date(),
                                        created_at__date__lte=today)
        Three_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                          created_at__date__lte=today)
        Six_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                        created_at__date__lte=today)
        One_Y = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_Y_past.date(),
                                        created_at__date__lte=today)
        All = FeedBack.objects.filter(Team_id__in=teams_list)

    elif type == 'user-teams':
        teams_list = TeamMembers.objects.filter(member_id=type_id).values('team')
        One_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_W_past.date(),
                                        created_at__date__lte=today)
        Two_W = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_W_past.date(),
                                        created_at__date__lte=today)
        One_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_M_past.date(),
                                        created_at__date__lte=today)
        Two_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Two_M_past.date(),
                                        created_at__date__lte=today)
        Three_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                          created_at__date__lte=today)
        Six_M = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=Three_M_past.date(),
                                        created_at__date__lte=today)
        One_Y = FeedBack.objects.filter(Team_id__in=teams_list, created_at__date__gte=One_Y_past.date(),
                                        created_at__date__lte=today)
        All = FeedBack.objects.filter(Team_id__in=teams_list)

    if One_W.count() > 0:
        for f in One_W:
            One_week = {
                "score": f.score,
                "created_at": f.created_at.date().strftime("%b %d %Y"),
                "month": f.month,
                "sprint": f.Sprint.name,
                "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
            }
            one_week_list.append(One_week)
        avg = average(one_week_list)
        one_week_list.append(avg)
    if Two_W.count() > 0:
        print(Two_W.count())
        for f in Two_W:
            Two_Week = {
                "score": f.score,
                "created_at": f.created_at.date().strftime("%b %d %Y"),
                "month": f.month,
                "sprint": f.Sprint.name,
                "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
            }
            two_week_list.append(Two_Week)
        print(two_week_list)
        avg = average(two_week_list)
        two_week_list.append(avg)
    if One_M.count() > 0:
        for f in One_M:
            One_Month = {
                "score": f.score,
                "created_at": f.created_at.date().strftime("%b %d %Y"),
                "month": f.month,
                "sprint": f.Sprint.name,
                "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
            }
            one_month_list.append(One_Month)
        avg = average(one_month_list)
        one_month_list.append(avg)
    if Two_M.count() > 0:
        for f in Two_M:
            Two_Month = {
                "score": f.score,
                "created_at": f.created_at.date().strftime("%b %d %Y"),
                "month": f.month,
                "sprint": f.Sprint.name,
                "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
            }
            two_month_list.append(Two_Month)
        avg = average(two_month_list)
        two_month_list.append(avg)
    if Three_M.count() > 0:
        for f in Three_M:
            Three_Month = {
                "score": f.score,
                "created_at": f.created_at.date().strftime("%b %d %Y"),
                "month": f.month,
                "sprint": f.Sprint.name,
                "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
            }
            three_month_list.append(Three_Month)
        avg = average(three_month_list)
        three_month_list.append(avg)
    if Six_M.count() > 0:
        for f in Six_M:
            Six_Month = {
                "score": f.score,
                "created_at": f.created_at.date().strftime("%b %d %Y"),
                "month": f.month,
                "sprint": f.Sprint.name,
                "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
            }
            six_month_list.append(Six_Month)
        avg = average(six_month_list)
        six_month_list.append(avg)

    if One_Y.count() > 0:
        for f in One_Y:
            One_Year = {
                "score": f.score,
                "created_at": f.created_at.date().strftime("%b %d %Y"),
                "month": f.month,
                "sprint": f.Sprint.name,
                "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
            }
            one_year_list.append(One_Year)
        avg = average(one_year_list)
        one_year_list.append(avg)
    if All.count() > 0:
        for f in All:
            All = {
                "score": f.score,
                "created_at": f.created_at.date().strftime("%b %d %Y"),
                "month": f.month,
                "sprint": f.Sprint.name,
                "sprint_start_date": f.Sprint.start_date.strftime("%b %d %Y"),
            }
            all_list.append(All)
        avg = average(all_list)
        all_list.append(avg)

    dict = {
        '1W': one_week_list,
        '2W': two_week_list,
        '1M': one_month_list,
        '2M': two_month_list,
        '3M': three_month_list,
        '6M': six_month_list,
        '1Y': one_year_list,
        'All': all_list,
    }

    return dict


def get_actionable_function(type, type_id, sprint_id):
    if type == 'team_id':
        topics_list = Bucket.objects.filter(Team=type_id, Tag='Negative').values_list('keyword',
                                                                                      flat=True).distinct()
        if not topics_list:
            return ' '
        else:
            summary = generate_negative_experiences(topics_list=topics_list)
            return summary

    elif type == 'product_area_id':
        prod_area_id = type_id
        teams_list = ProductAreaTeams.objects.filter(Product_Area=prod_area_id).values_list('Team', flat=True)
        if len(teams_list) > 1:
            topics_list = reduce(lambda Bucket, s: Bucket.filter(Team=s), teams_list,
                                 Bucket.objects.filter(Tag='Negative')).values_list('keyword',
                                                                                    flat=True).distinct()
            print(topics_list)

            if not topics_list:
                return ' '
            else:
                summary = generate_negative_experiences(topics_list=topics_list)
                return summary
        else:
            return ' '

    elif type == 'product_id':
        prod_id = type_id
        prod_area = ProductTeams.objects.filter(Product_id=prod_id).values('Product_Area')
        if len(prod_area) > 1:
            teams_list = ProductAreaTeams.objects.filter(Product_Area_id__in=prod_area).values_list('Team', flat=True)
            if len(teams_list) > 1:
                topics_list = reduce(lambda Bucket, s: Bucket.filter(Team=s), teams_list,
                                     Bucket.objects.filter(Tag='Negative')).values_list(
                    'keyword',
                    flat=True).distinct()
                if not topics_list:
                    return ' '
                else:
                    summary = generate_negative_experiences(topics_list=topics_list)
                    return summary
        else:
            return ' '

    elif type == 'enterprise':
        enterprise_id = Enterprise.objects.get(owner=type_id)
        prod_id = EnterpriseProducts.objects.filter(Enterprise=enterprise_id).values('Product')
        if len(prod_id) > 1:
            prod_area = ProductTeams.objects.filter(Product_id__in=prod_id).values('Product_Area')
            if len(prod_area) > 1:
                teams_list = ProductAreaTeams.objects.filter(Product_Area_id__in=prod_area).values_list('Team',
                                                                                                        flat=True)
                if len(teams_list) > 1:
                    topics_list = reduce(lambda Bucket, s: Bucket.filter(Team=s), teams_list,
                                         Bucket.objects.filter(Tag='Negative')).values_list(
                        'keyword',
                        flat=True).distinct()
                    if not topics_list:
                        return ' '
                    else:
                        summary = generate_negative_experiences(topics_list=topics_list)
                        return summary
        else:
            return ' '


def get_summary_function(type, type_id, sprint_id):
    if type == 'team_id':
        reviews = FeedBack.objects.filter(Team=type_id).values_list('feedback', flat=True).distinct()
        text = ' '
        texted = text.join(reviews)
        summary = gpt3_data_analysis(texted)
        if len(summary > 1):
            return summary
        else:
            return ' '

    elif type == 'product_area_id':
        prod_area_id = type_id
        teams_list = ProductAreaTeams.objects.filter(Product_Area=prod_area_id).values_list('Team', flat=True)
        if len(teams_list) > 1:
            reviews = list(FeedBack.objects.filter(Team__in=teams_list).values_list('feedback', flat=True).distinct())
            review_str = ' '
            for i in range(0, len(reviews)):
                if i == (len(reviews) - 1):
                    review_str += reviews[i]
                else:
                    review_str += reviews[i] + '\n'

            new_str = review_str.replace("\n", "\\n")
            summary = gpt3_data_analysis(new_str)
            if len(summary) > 1:
                return summary
        else:
            return ' '

    elif type == 'product_id':
        prod_id = type_id
        prod_area = ProductTeams.objects.filter(Product_id=prod_id).values('Product_Area')
        if len(prod_area) > 1:
            teams_list = ProductAreaTeams.objects.filter(Product_Area_id__in=prod_area).values_list('Team', flat=True)
            if len(teams_list) > 1:
                reviews = list(
                    FeedBack.objects.filter(Team__in=teams_list).values_list('feedback', flat=True).distinct())
                review_str = ' '
                for i in range(0, len(reviews)):
                    if i == (len(reviews) - 1):
                        review_str += reviews[i]
                    else:
                        review_str += reviews[i] + '\n'

                new_str = review_str.replace("\n", "\\n")
                summary = gpt3_data_analysis(new_str)
        else:
            return ' '

    elif type == 'enterprise':
        enterprise_id = Enterprise.objects.get(owner=type_id)
        prod_id = EnterpriseProducts.objects.filter(Enterprise=enterprise_id).values('Product')
        if len(prod_id) > 1:
            prod_area = ProductTeams.objects.filter(Product_id__in=prod_id).values('Product_Area')
            if len(prod_area) > 1:
                teams_list = ProductAreaTeams.objects.filter(Product_Area_id__in=prod_area).values_list('Team',
                                                                                                        flat=True)
                if len(teams_list) > 1:
                    reviews = list(
                        FeedBack.objects.filter(Team__in=teams_list).values_list('feedback', flat=True).distinct())
                    review_str = ' '
                    for i in range(0, len(reviews)):
                        if i == (len(reviews) - 1):
                            review_str += reviews[i]
                        else:
                            review_str += reviews[i] + '\n'

                    new_str = review_str.replace("\n", "\\n")
                    summary = gpt3_data_analysis(new_str)
                    if len(summary) > 1:
                        return summary
        else:
            return ' '
