import frontend.utils as utils


class DummyResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or []

    def json(self):
        return self._payload


def test_get_events_success(monkeypatch):
    def fake_get(url):
        assert url == f"{utils.API_URL}/calendar/"
        return DummyResponse(200, [{"title": "Hello"}])

    monkeypatch.setattr(utils.requests, "get", fake_get)
    assert utils.get_events() == [{"title": "Hello"}]


def test_get_events_failure_returns_empty(monkeypatch):
    def boom(url):
        raise RuntimeError("network down")

    monkeypatch.setattr(utils.requests, "get", boom)
    assert utils.get_events() == []


def test_shopping_list_and_delete(monkeypatch):
    captured = {}

    def fake_get(url):
        assert url == f"{utils.API_URL}/shopping/"
        return DummyResponse(200, [{"id": 1, "name": "Eggs"}])

    def fake_delete(url):
        captured["url"] = url
        return DummyResponse(200, {"message": "Item removed"})

    monkeypatch.setattr(utils.requests, "get", fake_get)
    monkeypatch.setattr(utils.requests, "delete", fake_delete)

    assert utils.get_shopping_list() == [{"id": 1, "name": "Eggs"}]
    utils.remove_shopping_item(1)
    assert captured["url"] == f"{utils.API_URL}/shopping/1"


def test_create_and_update_event_calls(monkeypatch):
    captured = {}

    def fake_post(url, json):
        captured["post"] = (url, json)
        return DummyResponse(200, {"ok": True})

    def fake_put(url, json):
        captured["put"] = (url, json)
        return DummyResponse(200, {"ok": True})

    monkeypatch.setattr(utils.requests, "post", fake_post)
    monkeypatch.setattr(utils.requests, "put", fake_put)

    utils.create_event({"title": "Study"})
    utils.update_event(5, {"title": "Updated"})

    assert captured["post"][0] == f"{utils.API_URL}/calendar/"
    assert captured["put"][0] == f"{utils.API_URL}/calendar/5"


def test_expenses_and_debts_helpers(monkeypatch):
    def fake_get(url):
        if url.endswith("/expenses/"):
            return DummyResponse(200, [{"title": "Lunch"}])
        if url.endswith("/expenses/debts"):
            return DummyResponse(200, [{"debtor": "Bob", "amount": 10}])
        return DummyResponse(200, [])

    def fake_post(url, json):
        return DummyResponse(200, {"id": 9})

    monkeypatch.setattr(utils.requests, "get", fake_get)
    monkeypatch.setattr(utils.requests, "post", fake_post)

    assert utils.get_expenses() == [{"title": "Lunch"}]
    assert utils.get_debts() == [{"debtor": "Bob", "amount": 10}]

    utils.add_expense({"title": "Dinner"})
    utils.add_reimbursement({"from_person": "Bob", "to_person": "Alice", "amount": 5})


def test_house_settings_helpers(monkeypatch):
    captured = {}

    def fake_get(url):
        return DummyResponse(200, {"name": "Test", "flatmates": ["A"]})

    def fake_post(url, json):
        captured["url"] = url
        captured["payload"] = json
        return DummyResponse(200, json)

    monkeypatch.setattr(utils.requests, "get", fake_get)
    monkeypatch.setattr(utils.requests, "post", fake_post)

    assert utils.get_house_settings() == {"name": "Test", "flatmates": ["A"]}

    utils.update_house_settings({"name": "New", "flatmates": ["A", "B"]})
    assert captured["url"] == f"{utils.API_URL}/house/"
    assert captured["payload"] == {"name": "New", "flatmates": ["A", "B"]}


def test_get_reimbursements_handles_failure(monkeypatch):
    def fake_get(url):
        raise RuntimeError("oops")

    monkeypatch.setattr(utils.requests, "get", fake_get)
    assert utils.get_reimbursements() == []