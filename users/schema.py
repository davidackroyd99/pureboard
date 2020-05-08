from django.contrib.auth import get_user_model

import graphene
from graphene_django import DjangoObjectType

from links.models import Vote

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
    
    def resolve_karma(parent, info):
        return sum(vote.score for vote in Vote.objects.filter(user_id=parent.id))

    karma = graphene.Int()

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    users = graphene.List(UserType, karma=graphene.Int())

    def resolve_users(self, info):
        users = get_user_model().objects.all()

        return users

    def resolve_me(self, info):
        user = info.context.user

        if user.is_anonymous:
            raise Exception('Not logged in!')

        return user


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        user = get_user_model()(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()

        return CreateUser(user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
