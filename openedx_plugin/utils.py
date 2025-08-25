# coding=utf-8
"""
written by:     Paul Okeke
                https://pauldiconline.com

date:           feb-2022

usage:          utility and convenience functions for openedx_plugin
"""
import json
from django.conf import settings
from types import SimpleNamespace
from unittest.mock import MagicMock
from collections.abc import MutableMapping
from dateutil.parser import parse, ParserError
from django.template.loader import render_to_string

from opaque_keys.edx.locator import CourseLocator

SENSITIVE_KEYS = [
    "password",
    "token",
    "client_id",
    "client_secret",
    "Authorization",
    "secret",
]


def flatten_dict(dictionary, parent_key="", sep="_"):
    """
    Generate a flatten dictionary-like object.
    Taken from:
    https://stackoverflow.com/a/6027615/16823624
    """
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


def serialize_course_key(inst, field, value):  # pylint: disable=unused-argument
    """
    Serialize instances of CourseLocator.
    When value is anything else returns it without modification.
    """
    if isinstance(value, CourseLocator):
        return str(value)
    return value


def objects_key_by(iter, key):
    index = {}
    for obj in iter:
        value = getattr(obj, key)
        index[value] = obj
    return index


def parse_date_string(date_string, raise_exception=False):
    try:
        return parse(date_string)
    except (TypeError, ParserError):
        if not raise_exception:
            return
        raise


def masked_dict(obj) -> dict:
    """
    To mask sensitive key / value in log entries.
    masks the value of specified key.
    obj: a dict or a string representation of a dict, or None
    """

    def redact(key: str, obj):
        if key in obj:
            obj[key] = "*** -- REDACTED -- ***"
        return obj

    obj = obj or {}
    obj = dict(obj)
    for key in SENSITIVE_KEYS:
        obj = redact(key, obj)
    return obj


class PluginJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding="utf-8")
        if isinstance(obj, MagicMock):
            return ""
        try:
            return json.JSONEncoder.default(self, obj)
        except Exception:  # noqa: B902
            # obj probably is not json serializable.
            return ""


def render_plugin_template(template_name, context=None, request=None):
    """
    Wrapper around render_to_string that injects a dummy request/context for Celery tasks.
    
    Usage:
        html = render_plugin_template(
            "student/edx_ace/accountactivation/email/body.html",
            context={"confirm_activation_link": "https://example.com/activate"}
        )
    """
    # Start with an empty context if none provided
    context = dict(context) if context else {}

    # Use actual request if available, otherwise inject dummy context
    if request is None:
        dummy_context = getattr(settings, "PLUGIN_DUMMY_CONTEXT", {})
        # Merge dummy_context into context without overwriting existing keys
        for key, value in dummy_context.items():
            context.setdefault(key, value)
    else:
        # Include request explicitly in context
        context.setdefault("request", request)
        context.setdefault("user", getattr(request, "user", None))
        context.setdefault("site", getattr(request, "site", None))

    return render_to_string(template_name, context=context)