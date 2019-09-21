import graphene

from ..queries import *
from ..mutations import *

schema = graphene.Schema(query=Query, mutation=MyMutations)
