import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q

from .models import Link, Vote, Profile
from users.schema import UserType

class LinkType(DjangoObjectType):
    class Meta:
        model = Link


class VoteType(DjangoObjectType):
    class Meta:
        model = Vote


class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile


class Query(graphene.ObjectType):
    links = graphene.List(LinkType, search=graphene.String(), 
        first=graphene.Int(), skip=graphene.Int())
    votes = graphene.List(VoteType)

    def resolve_links(self, info, search=None, first=None, skip=None, **kwargs):
        results = Link.objects.all()

        if search:
            ft = (
                Q(url__icontains=search) |
                Q(description__icontains=search)
            )
            results = results.filter(ft)

        if skip:
            results = results[skip:]

        if first:
            results = results[:first]

        return results

    def resolve_votes(self, info, **kwargs):
        return Vote.objects.all()


class CreateLink(graphene.Mutation):
    link = graphene.Field(LinkType)

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        poster = info.context.user or None

        link = Link(url=url, description=description, posted_by=poster)
        link.save()

        return CreateLink(link=link)


class CreateVote(graphene.Mutation):
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.Int(required=True)
        score = graphene.Int()

    def mutate(self, info, link_id, score=1):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('You must be logged to vote!')

        link = Link.objects.filter(id=link_id).first()
        if not link:
            raise Exception('Invalid Link!')

        vote = Vote.objects.filter(link=link, user=info.context.user).first()
        if not vote:
            Vote.objects.create(
                user=user,
                link=link,
                score=score
            )
        else:
            vote.score = score
            vote.save()

        return CreateVote(user=user, link=link)


class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()
