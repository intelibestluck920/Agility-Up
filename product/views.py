from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from permissions.permissions import IsProduct, IsProductArea, IsEnterprise
from rest_framework import status

from rest_framework.response import Response
from .serializers import *
from .models import ProductArea, ProductAreaMembers, ProductMembers, Product, ProductTeams, ProductMembers, \
    Enterprise, EnterpriseProducts

from core.serializers import TeamSerializer
from core.views import get_history_func
from core.models import Bucket
from core.serializers import BucketSerializer
from invites.serializers import ProductInviteSerializer
from invites.models import Invite
from django.core.mail import send_mail
from permissions.models import assigned_permissions
from core.views import get_actionable_function, get_summary_function


# Create your views here.


class ProductAreaCreate(APIView):
    permission_classes = (IsAuthenticated, IsProductArea)

    def post(self, request):
        serializer = CreateProductAreaSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            prod_area = serializer.save(product_area_creator=request.user, product_area_lead=request.user)
            ProductAreaMembers.objects.create(User=request.user, Product_Area_id=prod_area.id)
            return Response(serializer.data)


class ProductAreaList(APIView):
    permission_classes = (IsAuthenticated, IsProductArea)

    def get(self, request, ):
        if request.query_params.get('prod-area-id'):
            print('===================')
            obj = ProductArea.objects.get(id=request.query_params.get('prod-area-id'))
            teams_id = ProductAreaTeams.objects.filter(Product_Area_id=obj.id).values('Team')
            teams = Team.objects.filter(id__in=teams_id)
            buckets_obj = Bucket.objects.filter(Team__in=teams_id)
            buck_serialzier = BucketSerializer(buckets_obj, many=True)
            teams_list = []
            total_members = ProductAreaMembers.objects.filter(Product_Area_id=obj.id).count()
            members = ProductAreaMembers.objects.filter(Product_Area_id=obj.id).values('User')
            id_list = []
            for member in members:
                id_list.append(member['User'])
            members_data = User.objects.filter(id__in=id_list).values('id', 'email')
            for t in teams:
                dict = {
                    'id': t.id,
                    'name': t.name,
                    'history': get_history_func(type='team_id', type_id=t.id)
                }
                teams_list.append(dict)

            context = {
                'id': obj.id,
                'name': obj.name,
                'total_members': total_members,
                'members': members_data,
                'product_area_creator': obj.product_area_creator.id,
                'product_area_lead': obj.product_area_lead.id,
                'teams': teams_list,
                'accumulative_history': get_history_func(type='product_area_id', type_id=obj.id),
                'buckets': buck_serialzier.data,
            }
            return Response(context)
        else:
            obj = ProductAreaMembers.objects.select_related('Product_Area').filter(User=request.user)
            product_area_list = []
            for o in obj:
                dict = {
                    'id': o.Product_Area.id,
                    'name': o.Product_Area.name,
                    'product_area_creator': o.Product_Area.product_area_creator.id,
                    'product_area_lead': o.Product_Area.product_area_lead.id,
                    'history': get_history_func(type='product_area_id', type_id=o.Product_Area.id)
                }
                product_area_list.append(dict)

            context = {
                'product_areas': product_area_list,
                'accumulative_history': get_history_func(type='user-product-area', type_id=request.user.id)
            }
            return Response(context)


class ProductAreaView(APIView):
    permission_classes = (IsAuthenticated, IsProductArea)

    def put(self, request, pk):
        obj = ProductArea.objects.get(id=pk)
        if request.user.id == obj.product_area_lead.id or request.user.id == obj.product_area_creator.id:
            serializer = ListProductAreaSerializer(obj, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk):
        obj = ProductArea.objects.get(id=pk)
        if request.user.id == obj.product_area_lead.id or request.user.id == obj.product_area_creator.id:
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class ProductAreaTeamsView(APIView):
    permission_classes = (IsAuthenticated, IsProductArea)

    def post(self, request, pk):
        serializer = ProductAreaTeamsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                ProductAreaTeams.objects.create(Team_id=request.data['Team'], Product_Area_id=pk)
            except:
                pass

            return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        serializer = ProductAreaTeamsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                ProductAreaTeams.objects.get(Team_id=request.data['Team'], Product_Area_id=pk).delete()
            except:
                pass

            return Response(status=status.HTTP_204_NO_CONTENT)


class ProductCreate(APIView):
    permission_classes = (IsAuthenticated, IsProduct)

    def post(self, request):
        serializer = CreateProductSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            product = serializer.save(product_creator=request.user, product_lead=request.user)
            ProductMembers.objects.create(User=request.user, Product_id=product.id)
            return Response(serializer.data)


class ProductList(APIView):
    permission_classes = (IsAuthenticated, IsProduct)

    def get(self, request, ):
        if request.query_params.get('prod-id'):
            obj = Product.objects.get(id=request.query_params.get('prod-id'))
            total_members = ProductMembers.objects.filter(Product_id=obj.id).count()
            members = ProductMembers.objects.filter(Product_id=obj.id).values('User')
            id_list = []
            for member in members:
                id_list.append(member['User'])
            members_data = User.objects.filter(id__in=id_list).values('id', 'email')
            product_area_id = ProductTeams.objects.filter(Product_id=obj.id).values('Product_Area')
            product_area_list = ProductArea.objects.filter(id__in=product_area_id)
            teams_id = ProductAreaTeams.objects.filter(Product_Area_id__in=product_area_list.values('id')).values(
                'Team')
            buckets_obj = Bucket.objects.filter(Team__in=teams_id)
            buck_serialzier = BucketSerializer(buckets_obj, many=True)
            product_areas = []
            for prod in product_area_list:
                dict = {
                    'id': prod.id,
                    'name': prod.name,
                    'product_area_creator': prod.product_area_creator.id,
                    'product_area_lead': prod.product_area_lead.id,
                    'history': get_history_func(type='product_area_id', type_id=prod.id)
                }
                product_areas.append(dict)
            history = get_history_func(type='product_id', type_id=obj.id)
            context = {
                'id': obj.id,
                'name': obj.name,
                'total_members': total_members,
                'members': members_data,
                'product_creator': obj.product_creator.id,
                'product_lead': obj.product_lead.id,
                'product_areas': product_areas,
                'accumulative_history': history,
                'buckets': buck_serialzier.data,
            }
            return Response(context)

        else:
            obj = ProductMembers.objects.select_related('Product').filter(User=request.user)
            products = []
            for o in obj:
                dict = {
                    'id': o.Product.id,
                    'name': o.Product.name,
                    'product_creator': o.Product.product_creator.id,
                    'product_lead': o.Product.product_lead.id,
                    'history': get_history_func(type='product_id', type_id=o.Product.id),
                }
                products.append(dict)
            context = {
                'context': products,
                'accumulative_history': get_history_func(type='user-products', type_id=request.user.id)
            }
            return Response(context)


class ProductView(APIView):
    permission_classes = (IsAuthenticated, IsProduct)

    def put(self, request, pk):
        obj = Product.objects.get(id=pk)
        if request.user.id == obj.product_lead.id or request.user.id == obj.product_creator.id:
            serializer = ListProductSerializer(obj, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk):
        obj = Product.objects.get(id=pk)
        if request.user.id == obj.product_lead.id or request.user.id == obj.product_creator.id:
            Product.objects.get(id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class ProductTeamsView(APIView):
    permission_classes = (IsAuthenticated, IsProduct)

    def post(self, request, pk):
        serializer = ProductTeamsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                ProductTeams.objects.create(Product_Area_id=request.data['Product_Area'], Product_id=pk)
            except:
                pass

            return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        serializer = ProductTeamsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                ProductTeams.objects.get(Product_Area_id=request.data['Product_Area'], Product_id=pk).delete()
            except:
                pass

            return Response(status=status.HTTP_204_NO_CONTENT)


class EnterpriseProductsAdd(APIView):
    permission_classes = (IsAuthenticated, IsEnterprise)

    def post(self, request):
        serializer = EnterpriseProductsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            prod_id = request.data['Product']
            for x in prod_id:
                prod = Product.objects.get(id=x)
                try:
                    EnterpriseProducts.objects.create(Enterprise=request.user.Enterprise, Product=prod)
                except:
                    pass

            return Response(status=status.HTTP_201_CREATED)

    def delete(self, request):
        serializer = EnterpriseProductsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            prod_id = request.data['Product']
            for x in prod_id:
                EnterpriseProducts.objects.filter(Enterprise=request.user.Enterprise, Product_id=x).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)


class EnterpriseList(APIView):
    permission_classes = (IsAuthenticated, IsEnterprise)

    def get(self, request):
        obj = EnterpriseProducts.objects.filter(Enterprise__owner=request.user).values('Product')
        obj_pro = Product.objects.filter(id__in=obj)
        ent = request.user.Enterprise.id
        # serializer = ListProductSerializer(obj_pro, many=True)
        history = get_history_func(type='enterprise', type_id=ent)
        products = []
        for obj in obj_pro:
            dict = {
                'id': obj.id,
                'name': obj.name,
                'product_creator': obj.product_creator.id,
                'product_lead': obj.product_lead.id,
                'history': get_history_func(type='product_id', type_id=obj.id)
            }
            products.append(dict)
        context = {
            'context': products,
            'accumulative_history': history,
        }
        return Response(context)
        # return Response(serializer.data)


# product area and product members

class ProductAreaMembersView(APIView):
    permission_classes = (IsAuthenticated, IsProductArea)

    def get(self, request):
        prod_area = request.query_params.get('prod_area')
        obj = ProductAreaMembers.objects.filter(Product_Area_id=prod_area).order_by('User')
        user = User.objects.filter(id__in=obj.values_list('User')).order_by('id')
        userserializer = UserInforSerializer(user, many=True)
        objserializer = ProductAreaMembersSerializer(obj, many=True)
        context = {
            'members': userserializer.data,
            'productareamembers': objserializer.data,
        }
        return Response(context)

    def post(self, request):
        serializer = ProductAreaMembersSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            prod_area_id = serializer.validated_data['Product_Area']
            user_id = serializer.validated_data['User']
            user = User.objects.get(id=user_id.id)
            prod_area = ProductArea.objects.get(id=prod_area_id.id)
            serializer.save()
            subject = f'added to {prod_area.name}'
            message = f'Welcome, you have been added to {prod_area.name}, click the link below to continue. \n \
                                    http://dev.agilityup.ai/productarea/join/{prod_area.id}/{prod_area.slug}'  # todo change url to frontend production
            to = []
            to.append(user.email)
            from_email = 'agility.up.ai.test@gmail.com'
            send_mail(
                subject,
                message,
                from_email,
                to,
                fail_silently=False
            )

        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request):
        obj = request.query_params.get('id')
        ProductAreaMembers.objects.get(id=obj).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductMembersView(APIView):
    permission_classes = (IsAuthenticated, IsProductArea)

    def get(self, request):
        product = request.query_params.get('product')
        obj = ProductMembers.objects.filter(Product_id=product).order_by('User')
        user = User.objects.filter(id__in=obj.values_list('User')).order_by('id')
        userserializer = UserInforSerializer(user, many=True)
        objserialzier = ProductMembersSerializer(obj, many=True)
        context = {
            'members': userserializer.data,
            'productmembers': objserialzier.data,
        }
        return Response(context)

    def post(self, request):
        serializer = ProductMembersSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            prod_id = serializer.validated_data['Product']
            user_id = serializer.validated_data['User']
            print(user_id)
            user = User.objects.get(id=user_id.id)
            prod = Product.objects.get(id=prod_id.id)
            serializer.save()
            subject = f'added to {prod.name}'
            message = f'Welcome, you have been added to {prod.name}, click the link below to continue. \n \
                        http://dev.agilityup.ai/product/join/{prod.id}/{prod.slug}'  # todo change url to frontend production
            to = []
            to.append(user.email)
            from_email = 'agility.up.ai.test@gmail.com'
            send_mail(
                subject,
                message,
                from_email,
                to,
                fail_silently=False
            )
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request):
        obj = request.query_params.get('id')
        ProductMembers.objects.get(id=obj).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductsInvites(APIView):
    # permission_classes = (IsAuthenticated, IsProduct)

    def post(self, request):
        serializer = ProductInviteSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            product = serializer.validated_data['product']
            product_area = serializer.validated_data['product_area']
            if product is None:
                prod_area = ProductArea.objects.get(id=product_area)
                subject = f'invited to {prod_area.name}'
                message = f'Welcome, you have been invited to AgilityUp, click the link below to join. \n \
                                        http://dev.agilityup.ai/productarea/join/{prod_area.id}/{prod_area.slug}'  # todo change url to frontend production
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
                    invitee=email, Inviter_id=request.user.id, product_Area_id=product_area
                )
                assigned_permissions.objects.create(email=email, user_exists=False, product_area=True)
            elif product_area is None:
                prod = Product.objects.get(id=product)
                subject = f'invited to {prod.name}'
                message = f'Welcome, you have been invited to AgilityUp, click the link below to join. \n \
                            http://dev.agilityup.ai/product/join/{prod.id}/{prod.slug}'  # todo change url to frontend production
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
                    invitee=email, Inviter_id=request.user.id, product_id=product
                )
                assigned_permissions.objects.create(email=email, user_exists=False, product=True)

            return Response(status=status.HTTP_201_CREATED)


class ProductAreaJoin(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        response = {
            'Detail': 'user added successfully'
        }
        try:
            obj = Invite.objects.get(ProductArea_id=pk, invitee=request.user.email)
            obj.accepted = True
        except:
            return Response(response)
        return Response(response)


class ProductJoin(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        response = {
            'Detail': 'user added successfully'
        }
        try:
            obj = Invite.objects.get(Product_id=pk, invitee=request.user.email)
            obj.accepted = True
        except:
            return Response(response)
        return Response(response)


class Actionable(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        type = request.query_params.get('type')
        type_id = request.query_params.get('type_id')
        sprint_id = request.query_params.get('sprint_id')
        summary = get_actionable_function(type, type_id, sprint_id)
        print(summary)
        return Response(summary)


class Summary(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        type = request.query_params.get('type')
        type_id = request.query_params.get('type_id')
        sprint_id = request.query_params.get('sprint_id')
        summary = get_summary_function(type, type_id, sprint_id)
        print(summary)
        return Response(summary)
