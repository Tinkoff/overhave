from faker import Faker

from overhave.storage.feature_type import FeatureTypeStorage


class TestFeatureTypeStorage:
    """ Integration tests for :class:`FeatureTypeStorage`. """

    def test_get_default_feature_type(self, test_feature_type_storage: FeatureTypeStorage, faker: Faker):
        feature_type_model = test_feature_type_storage.get_default_feature_type()
        assert feature_type_model is not None
        name = faker.word()
        feature_type_model.name = name
        assert feature_type_model.name == name
