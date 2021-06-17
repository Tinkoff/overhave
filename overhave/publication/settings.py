from overhave.base_settings import BaseOverhavePrefix
from overhave.publication.objects import PublicationManagerType


class PublicationSettings(BaseOverhavePrefix):
    """ Publication settings where you can specify publcation manager and its behavior. """

    # Choose gitlab or stash as a publication manager
    publication_manager_type: str = PublicationManagerType.GITLAB
