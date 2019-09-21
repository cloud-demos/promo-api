import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from domain import models
from domain import prom_code


class PromCodeInput(graphene.InputObjectType):
    event_id = graphene.Int(required=True)
    page = graphene.Int()
    page_length = graphene.Int()


class PromCodeObject(SQLAlchemyObjectType):
    class Meta:
        model = models.PromCode
        interfaces = (graphene.relay.Node, )


class PromCodeOutput(graphene.ObjectType):
    items = graphene.List(PromCodeObject)
    pages = graphene.Int()


class Query(graphene.ObjectType):

    promo_codes = graphene.Field(PromCodeOutput,
                                 params=PromCodeInput(required=True))
    active_promo_codes = graphene.Field(PromCodeOutput,
                                        params=PromCodeInput(required=True))

    def resolve_promo_codes(self, info, params):
        """
query first_query{
  promoCodes(params: {eventId: 1, page: 4, pageLength: 2}){
    items{
      credit
      code
      eventId
      expirationTime
      radius
    }
    pages

  }
}

{
  "data": {
    "promoCodes": {
      "items": [
        {
          "credit": 10,
          "code": "eBYcThJA0lYF",
          "eventId": 1,
          "expirationTime": "2019-09-14T21:35:09.172000",
          "radius": 1212.88
        },
        {
          "credit": 10,
          "code": "LUm2lisVDAvr",
          "eventId": 1,
          "expirationTime": "2019-09-14T21:35:09.172000",
          "radius": 1212.88
        }
      ],
      "pages": 48
    }
  }
}
        :param info:
        :param params:
        :return:
        """

        page = params.page or 1
        page_length = params.page_length or 10
        res = prom_code.get_all_promo_codes(params.event_id, page, page_length)
        return PromCodeOutput(res.items, res.pages)

    def resolve_active_promo_codes(self, info, params):
        """
query second_query{
  activePromoCodes(params: {eventId: 1, page: 2, pageLength: 3}){
    items{
      credit
      code
      eventId
      expirationTime
      radius
    }
    pages

  }
}
        """
        page = params.page or 1
        page_length = params.page_length or 10
        res = prom_code.get_active_promo_codes(params.event_id, page,
                                               page_length)
        return PromCodeOutput(res.items, res.pages)
