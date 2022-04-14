from typing import List, Mapping, Sequence, cast

import pytest
from faker import Faker

from overhave.storage import FeatureTypeName
from tests.objects import get_test_feature_extractor


@pytest.fixture()
def test_repository_id_or_name(faker: Faker) -> str:
    return cast(str, faker.word())


@pytest.fixture()
def test_project_key(faker: Faker) -> str:
    return cast(str, faker.word()).upper()


@pytest.fixture()
def test_target_branch(faker: Faker) -> str:
    return cast(str, faker.word())


@pytest.fixture()
def test_default_reviewers(faker: Faker) -> Sequence[str]:
    return cast(Sequence[str], faker.words(faker.random.randint(1, 10)))


@pytest.fixture()
def test_reviewers_mapping(faker: Faker) -> Mapping[FeatureTypeName, List[str]]:
    return {
        feature_type: cast(List[str], faker.words(faker.random.randint(1, 10)))
        for feature_type in get_test_feature_extractor().feature_types
    }
