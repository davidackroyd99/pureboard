import graphene
from graphene_django import DjangoObjectType

from .models import Link, Vote


class LinkType(DjangoObjectType):
    class Meta:
        model = Link


class Query(graphene.ObjectType):
    links = graphene.List(LinkType)

    def resolve_links(self, info, **kwargs):
        return Link.objects.all()


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


class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
