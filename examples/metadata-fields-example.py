"""Worked example: give each metadata key its own span attribute.

The problem: the SDK writes everything you pass as metadata (user_id, a business
unit, a channel, ...) into ONE span attribute, `splunk_ao.metadata`, as a JSON
string. In the console that is a single field, so you can only match it with
"contains". Filtering and grouping by user_id in Trends does not work cleanly.

The fix: wrap `splunk_ao.converter.attribute_mapping.set_common_attributes`. Let
the original run, read the JSON back out of `splunk_ao.metadata`, write one
attribute per key, and delete the blob. Each key then shows up as its own field.

Use it in your agent:
    1. Copy `export_metadata_fields()` and `_attribute_value()` into app.py.
    2. Call `export_metadata_fields()` once at startup, before the first trace.
    3. Pass metadata as you already do, for example
       RunnableConfig(callbacks=[callback], metadata={"user_id": user_id}).

See the effect without sending anything (no credentials needed). From the
agent's folder, with its venv active:
    python ../../examples/metadata-fields-example.py

Notes:
- It patches the module attribute, not a copy of the function. The SDK looks the
  name up in the module at call time, so the patch applies to every span.
- The flag on the replacement makes a second call do nothing, so calling it per
  request is harmless.
- It edits the attribute dict while the SDK is still building it. There is no
  supported hook after that point.
- A metadata key that matches an SDK attribute name would overwrite it. Use plain
  keys such as `user_id` or `business_unit`.
- This wraps an SDK internal and works around a known product issue. It was
  written against splunk-ao 0.6.1. Re-check it after an SDK upgrade, and remove
  it once the product writes one attribute per key itself.
"""
import json


def _attribute_value(value):
    """Span attributes hold str, int, float or bool. Anything else becomes JSON text."""
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return value
    return json.dumps(value, separators=(",", ":"), sort_keys=True, default=str)


def export_metadata_fields() -> None:
    from splunk_ao.converter import attribute_mapping as mapping

    if getattr(mapping.set_common_attributes, "_exports_metadata_fields", False):
        return
    original = mapping.set_common_attributes

    def set_common_attributes(attrs, span, session_id=None):
        original(attrs, span, session_id)
        blob = attrs.get("splunk_ao.metadata")
        if not isinstance(blob, str):
            return
        try:
            parsed = json.loads(blob)
        except json.JSONDecodeError:
            return
        if not isinstance(parsed, dict):
            return
        for key, value in parsed.items():
            attrs[str(key)] = _attribute_value(value)
        attrs.pop("splunk_ao.metadata", None)

    set_common_attributes._exports_metadata_fields = True
    mapping.set_common_attributes = set_common_attributes


if __name__ == "__main__":
    from types import SimpleNamespace

    from splunk_ao.converter import attribute_mapping as mapping

    # Stand-in for a span: only the fields set_common_attributes reads.
    span = SimpleNamespace(
        redacted_input=None, redacted_output=None, tags=None, status_code=None,
        user_metadata={"user_id": "E-10001", "business_unit": "retail"},
    )

    def show(label):
        attrs = {}
        mapping.set_common_attributes(attrs, span)
        print(f"{label}: {attrs}")

    show("before")
    export_metadata_fields()
    show("after ")
