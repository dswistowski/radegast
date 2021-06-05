import pytest

from examples.reqres import ReqRes, User, UserDetail


@pytest.fixture
def client():
    return ReqRes()


def test_reg_res_client_should_be_able_to_list_users(client: ReqRes):
    users = client.users()
    assert users.page == 1
    assert len(users.data)


def test_reg_res_client_should_be_able_to_get_second_page(client: ReqRes):
    users = client.users.params(page=2)()
    assert users.page == 2


def test_reg_res_client_per_page(client: ReqRes):
    users = client.users.params(per_page=2)()
    assert len(users.data) == 2


def test_rag_res_one_user(client: ReqRes):
    user = client.user(id=3)
    assert isinstance(user, UserDetail)
