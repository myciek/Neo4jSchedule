from services.accounts_service import create_user


def test_new_user():
    user = create_user("Maciej Mycielski", "example@c.pl", False, "123qwe")
    assert user.name == "Maciej Mycielski"
    assert user.email == "example@c.pl"
    assert user.password != "123qwe"
    assert user.student == True
