import json
from types import SimpleNamespace

import backend.classifier as classifier_module


class DummyResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class DummyInferenceClient:
    def __init__(self, config, service_endpoint=None):
        self.config = config
        self.service_endpoint = service_endpoint

    def chat(self, details):
        assert self.service_endpoint == "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
        assert details.compartment_id == "ocid1.compartment.oc1..demo"
        assert details.serving_mode.model_id == "cohere.command-latest"
        return SimpleNamespace(
            data=SimpleNamespace(
                chat_response=SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(
                                content=[
                                    SimpleNamespace(
                                        text=json.dumps(
                                            {
                                                "intent": "member_preparation",
                                                "subject_type": "member",
                                                "member_type": "autonomous_database",
                                                "confidence": 0.88,
                                                "reason": "the request is asking about Autonomous Database preparation",
                                            }
                                        )
                                    )
                                ]
                            )
                        )
                    ]
                )
            )
        )


def test_ai_classifier_uses_direct_oci_inference(monkeypatch) -> None:
    monkeypatch.setenv("AI_CLASSIFIER_ENABLED", "true")
    monkeypatch.delenv("AI_CLASSIFIER_URL", raising=False)
    monkeypatch.delenv("AI_CLASSIFIER_MODEL", raising=False)
    monkeypatch.delenv("AI_CLASSIFIER_OCI_ENDPOINT_ID", raising=False)

    def fake_from_file(*_args, **_kwargs):
        return {
            "region": "us-chicago-1",
            "user": "ocid1.user.oc1..demo",
            "tenancy": "ocid1.tenancy.oc1..demo",
            "fingerprint": "demo",
            "key_file": "/tmp/demo.pem",
            "oci_genai_endpoint": '"https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",',
            "model_id": '"cohere.command-latest",',
            "oci_compartment_ocid": '"ocid1.compartment.oc1..demo", # comment',
        }

    monkeypatch.setattr(classifier_module.oci.config, "from_file", fake_from_file)
    monkeypatch.setattr(classifier_module, "GenerativeAiInferenceClient", DummyInferenceClient)

    result = classifier_module.classify_request(
        "I need to understand what needs to be in place before we use Autonomous Database with FSDR."
    )

    assert result.intent == "member_preparation"
    assert result.member_type == "autonomous_database"
    assert result.best_skill == "skills/prerequisites/members/fsdr-prepare-autonomous-database.md"
    assert result.reason.startswith("ai classifier:")
    assert result.confidence == 0.88


def test_ai_classifier_uses_model_response(monkeypatch) -> None:
    monkeypatch.setenv("AI_CLASSIFIER_ENABLED", "true")
    monkeypatch.setenv("AI_CLASSIFIER_URL", "https://example.invalid/v1/chat/completions")
    monkeypatch.setenv("AI_CLASSIFIER_MODEL", "demo-router-model")
    monkeypatch.delenv("AI_CLASSIFIER_API_KEY", raising=False)
    monkeypatch.setenv("AI_CLASSIFIER_OCI_ENDPOINT_ID", "")
    monkeypatch.setenv("AI_CLASSIFIER_OCI_GENAI_ENDPOINT", "")
    monkeypatch.setenv("AI_CLASSIFIER_OCI_MODEL_ID", "")
    monkeypatch.setenv("AI_CLASSIFIER_OCI_COMPARTMENT_ID", "")
    monkeypatch.setenv("OCI_CONFIG_PATH", "/tmp/fsdr-missing-oci-config")

    def fake_urlopen(request, timeout):
        assert request.full_url == "https://example.invalid/v1/chat/completions"
        body = json.loads(request.data.decode("utf-8"))
        assert body["model"] == "demo-router-model"
        return DummyResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "intent": "tenancy_onboarding",
                                    "subject_type": "tenancy",
                                    "member_type": "none",
                                    "confidence": 0.91,
                                    "reason": "the request asks how to begin in a tenancy",
                                }
                            )
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(classifier_module.urllib_request, "urlopen", fake_urlopen)

    result = classifier_module.classify_request("We are new to FSDR. What should we do first in this tenancy?")

    assert result.intent == "tenancy_onboarding"
    assert result.best_skill == "skills/tenancy/fsdr-tenancy-onboard.md"
    assert result.reason.startswith("ai classifier:")
    assert result.confidence == 0.91


def test_heuristic_classifier_routes_member_addition_to_member_preparation(monkeypatch) -> None:
    monkeypatch.setenv("AI_CLASSIFIER_ENABLED", "true")
    monkeypatch.setenv("AI_CLASSIFIER_URL", "https://example.invalid/v1/chat/completions")
    monkeypatch.setenv("AI_CLASSIFIER_MODEL", "demo-router-model")
    monkeypatch.setenv("AI_CLASSIFIER_OCI_ENDPOINT_ID", "")
    monkeypatch.setenv("AI_CLASSIFIER_OCI_GENAI_ENDPOINT", "")
    monkeypatch.setenv("AI_CLASSIFIER_OCI_MODEL_ID", "")
    monkeypatch.setenv("AI_CLASSIFIER_OCI_COMPARTMENT_ID", "")
    monkeypatch.setenv("OCI_CONFIG_PATH", "/tmp/fsdr-missing-oci-config")

    def fake_urlopen(_request, timeout):
        return DummyResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "intent": "not_a_real_intent",
                                    "subject_type": "general",
                                    "member_type": "none",
                                    "confidence": 0.99,
                                    "reason": "invalid taxonomy output",
                                }
                            )
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(classifier_module.urllib_request, "urlopen", fake_urlopen)

    result = classifier_module.classify_request("What can I do to add database to a DRPG?")

    assert result.intent == "member_preparation"
    assert result.member_type == "database"
    assert result.best_skill == "skills/prerequisites/members/fsdr-prepare-database.md"
    assert result.reason.startswith("heuristic classifier:")


def test_ai_classifier_falls_back_when_model_response_is_invalid(monkeypatch) -> None:
    monkeypatch.setenv("AI_CLASSIFIER_ENABLED", "true")
    monkeypatch.setenv("AI_CLASSIFIER_URL", "https://example.invalid/v1/chat/completions")
    monkeypatch.setenv("AI_CLASSIFIER_MODEL", "demo-router-model")
    monkeypatch.setenv("AI_CLASSIFIER_OCI_ENDPOINT_ID", "")
    monkeypatch.setenv("AI_CLASSIFIER_OCI_GENAI_ENDPOINT", "")
    monkeypatch.setenv("AI_CLASSIFIER_OCI_MODEL_ID", "")
    monkeypatch.setenv("AI_CLASSIFIER_OCI_COMPARTMENT_ID", "")
    monkeypatch.setenv("OCI_CONFIG_PATH", "/tmp/fsdr-missing-oci-config")

    def fake_urlopen(_request, timeout):
        return DummyResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "intent": "not_a_real_intent",
                                    "subject_type": "general",
                                    "member_type": "none",
                                    "confidence": 0.99,
                                    "reason": "invalid taxonomy output",
                                }
                            )
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(classifier_module.urllib_request, "urlopen", fake_urlopen)

    result = classifier_module.classify_request("What should I do to get my OKE environment ready for FSDR?")

    assert result.intent == "member_preparation"
    assert result.member_type == "oke"
    assert result.best_skill == "skills/prerequisites/members/fsdr-prepare-oke.md"
    assert result.reason.startswith("heuristic classifier:")
