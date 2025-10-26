import pytest

from clipify.pipelines.gemini_pipeline import call_gemini

class DummyProvider:
    def __init__(self, resp):
        self.resp = resp
    def get_response(self, prompt, retry_count=3):
        return self.resp

def test_call_gemini_with_mocked_provider(monkeypatch):
    # Mock get_ai_provider to return a dummy provider that returns valid JSON
    def fake_get_ai_provider(name, api_key, model=None):
        resp = {"choices":[{"message":{"content":'{"highlights":[{"title":"T","excerpt":"hello world"}]}'}}]}
        return DummyProvider(resp)

    monkeypatch.setattr('clipify.core.ai_providers.get_ai_provider', fake_get_ai_provider)

    res = call_gemini("hello world this is a transcript", clips=1)
    assert isinstance(res, dict)
    assert 'highlights' in res
    assert res['highlights'][0]['excerpt'] == 'hello world'
