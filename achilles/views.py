from django.http import HttpResponseBadRequest, HttpResponse
from django.conf import settings
from django.test.client import CONTENT_TYPE_RE

from achilles.common import achilles_renders
from achilles.actions import run_actions

import json


def endpoint(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    match = CONTENT_TYPE_RE.match(request.META['CONTENT_TYPE'])
    if match:
        charset = match.group(1)
    else:
        charset = settings.DEFAULT_CHARSET

    data = json.loads(request.body.decode(charset))
    run_actions(request, data)

    result = {}
    for (namespace, render) in achilles_renders().iteritems():
        result[namespace] = render(request)

    return HttpResponse(json.dumps(result), content_type="application/json")
