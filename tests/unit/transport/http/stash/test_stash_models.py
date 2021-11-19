import datetime

from overhave.transport import StashPrCreationResponse


class TestStashHttpClientModels:
    """Unit tests for :class:`StashHttpClient` models."""

    def test_pr_creation_response(self) -> None:
        response = StashPrCreationResponse.parse_obj(  # noqa: ECE001
            {
                "id": 270,
                "version": 0,
                "title": "BDD test scenario",
                "description": (
                    "Feature ID: 35. Type: 'chat'.\nCreated by: @user1 at 2020-01-17 11:48:51.154478+03:00.\n"
                    "Last edited by: @user2.\nTasks: PRJ-123\nPR from Test Run ID: 321. Executed by: @user3",
                ),
                "state": "OPEN",
                "open": True,
                "closed": False,
                "createdDate": 1614938899839,
                "updatedDate": 1614938899839,
                "fromRef": {
                    "id": "refs/heads/bdd-feature-35",
                    "displayId": "bdd-feature-35",
                    "latestCommit": "44cddbac06f27d06f69bb482e5cbf112c29ab976",
                    "repository": {
                        "slug": "bdd-features",
                        "id": 11412,
                        "name": "bdd-features",
                        "hierarchyId": "857525eb55888a32367d",
                        "scmId": "git",
                        "state": "AVAILABLE",
                        "statusMessage": "Available",
                        "forkable": False,
                        "project": {
                            "key": "PRJ",
                            "id": 435934,
                            "name": "My Best Project",
                            "public": False,
                            "type": "NORMAL",
                            "links": {"self": [{"href": "https://stash.mycompany.com/projects/PRJ"}]},
                        },
                        "public": False,
                        "links": {
                            "clone": [
                                {"href": "ssh://git@stash.mycompany.com:8895/PRJ/bdd-features.git", "name": "ssh"},
                                {"href": "https://stash.mycompany.com/scm/PRJ/bdd-features.git", "name": "http"},
                            ],
                            "self": [{"href": "https://stash.mycompany.com/projects/PRJ/repos/bdd-features/browse"}],
                        },
                    },
                },
                "toRef": {
                    "id": "refs/heads/master",
                    "displayId": "master",
                    "latestCommit": "2cb5d23612df0f62f1377881adc213bac04eec6e",
                    "repository": {
                        "slug": "bdd-features",
                        "id": 11412,
                        "name": "bdd-features",
                        "hierarchyId": "857525eb55888a32367d",
                        "scmId": "git",
                        "state": "AVAILABLE",
                        "statusMessage": "Available",
                        "forkable": False,
                        "project": {
                            "key": "PRJ",
                            "id": 435934,
                            "name": "My Best Project",
                            "public": False,
                            "type": "NORMAL",
                            "links": {"self": [{"href": "https://stash.mycompany.com/projects/PRJ"}]},
                        },
                        "public": False,
                        "links": {
                            "clone": [
                                {"href": "ssh://git@stash.mycompany.com:8895/PRJ/bdd-features.git", "name": "ssh"},
                                {"href": "https://stash.mycompany.com/scm/PRJ/bdd-features.git", "name": "http"},
                            ],
                            "self": [{"href": "https://stash.mycompany.com/projects/PRJ/repos/bdd-features/browse"}],
                        },
                    },
                },
                "locked": False,
                "author": {
                    "user": {
                        "name": "author",
                        "emailAddress": "",
                        "id": 4298534,
                        "displayName": "author",
                        "active": True,
                        "slug": "author",
                        "type": "NORMAL",
                        "links": {"self": [{"href": "https://stash.mycompany.com/users/author"}]},
                    },
                    "role": "AUTHOR",
                    "approved": False,
                    "status": "UNAPPROVED",
                },
                "reviewers": [
                    {
                        "user": {
                            "name": "user3",
                            "emailAddress": "user3@mycompany.com",
                            "id": 3919394,
                            "displayName": "kek",
                            "active": True,
                            "slug": "user3",
                            "type": "NORMAL",
                            "links": {"self": [{"href": "https://stash.mycompany.com/users/user3"}]},
                        },
                        "role": "REVIEWER",
                        "approved": False,
                        "status": "UNAPPROVED",
                    },
                    {
                        "user": {
                            "name": "user4",
                            "emailAddress": "user4@mycompany.com",
                            "id": 4384045,
                            "displayName": "kek",
                            "active": True,
                            "slug": "user4",
                            "type": "NORMAL",
                            "links": {"self": [{"href": "https://stash.mycompany.com/users/user4"}]},
                        },
                        "role": "REVIEWER",
                        "approved": False,
                        "status": "UNAPPROVED",
                    },
                    {
                        "user": {
                            "name": "user5",
                            "emailAddress": "user5@mycompany.com",
                            "id": 2522559,
                            "displayName": "kek",
                            "active": True,
                            "slug": "user5",
                            "type": "NORMAL",
                            "links": {"self": [{"href": "https://stash.mycompany.com/users/user5"}]},
                        },
                        "role": "REVIEWER",
                        "approved": False,
                        "status": "UNAPPROVED",
                    },
                    {
                        "user": {
                            "name": "user6",
                            "emailAddress": "user6@mycompany.com",
                            "id": 4384295,
                            "displayName": "kek",
                            "active": True,
                            "slug": "user6",
                            "type": "NORMAL",
                            "links": {"self": [{"href": "https://stash.mycompany.com/users/user6"}]},
                        },
                        "role": "REVIEWER",
                        "approved": False,
                        "status": "UNAPPROVED",
                    },
                    {
                        "user": {
                            "name": "user7",
                            "emailAddress": "user7@mycompany.com",
                            "id": 1831652,
                            "displayName": "kek",
                            "active": True,
                            "slug": "user7",
                            "type": "NORMAL",
                            "links": {"self": [{"href": "https://stash.mycompany.com/users/user7"}]},
                        },
                        "role": "REVIEWER",
                        "approved": False,
                        "status": "UNAPPROVED",
                    },
                    {
                        "user": {
                            "name": "user8",
                            "emailAddress": "user8@mycompany.com",
                            "id": 4436648,
                            "displayName": "kek",
                            "active": True,
                            "slug": "user8",
                            "type": "NORMAL",
                            "links": {"self": [{"href": "https://stash.mycompany.com/users/user8"}]},
                        },
                        "role": "REVIEWER",
                        "approved": False,
                        "status": "UNAPPROVED",
                    },
                    {
                        "user": {
                            "name": "user9",
                            "emailAddress": "user9@mycompany.com",
                            "id": 3855918,
                            "displayName": "lel",
                            "active": True,
                            "slug": "user9",
                            "type": "NORMAL",
                            "links": {"self": [{"href": "https://stash.mycompany.com/users/user9"}]},
                        },
                        "role": "REVIEWER",
                        "approved": False,
                        "status": "UNAPPROVED",
                    },
                ],
                "participants": [],
                "links": {
                    "self": [{"href": "https://stash.mycompany.com/projects/PRJ/repos/bdd-features/pull-requests/270"}]
                },
            }
        )
        assert response.title == "BDD test scenario"
        assert response.traceback is None
        assert response.created_date == datetime.datetime(2021, 3, 5, 10, 8, 19, 839000, tzinfo=datetime.timezone.utc)
        assert response.updated_date == datetime.datetime(2021, 3, 5, 10, 8, 19, 839000, tzinfo=datetime.timezone.utc)
        assert response.pull_request_url is None
