from django.conf import settings
from importlib import import_module

from achilles.common import BaseLibrary, achilles_data


class Library(BaseLibrary):
    """
    Action library holds a register of all defined actions

    Use it to define and register new actions, grouping them under
    a common namespace::

        from achilles import actions

        register = actions.Library('myapp')

        @register.action
        def foo(request, *args, **kwargs):
            # do stuff
            pass

    :param namespace: Unique namespace for this register
    """
    def __init__(self, namespace=None):
        BaseLibrary.__init__(self, namespace)

        # Provide action register
        self.action = self.register


def get(name):
    """
    Retrieve an action function with the given name. Example::

        actions.get('myapp:foo')

    :param name: Fully namespaced action name
    """
    # make sure all actions are loaded
    for app in settings.INSTALLED_APPS:
        try:
            import_module(app + '.actions')
        except ImportError:
            pass

    return Library.get_global(name)


def run_actions(request, actions):
    """
    Run the given list of actions sent by the client
    """
    data = achilles_data(request, 'actions', {})
    for a in actions:
        name = a['name']
        action = get(name)

        # run and save return value
        try:
            result = action(request, *a.get('args', []), **a.get('kwargs', {}))
            data[a['id']] = {
                'value': result
            }
        except Exception as e:
            # Mark as error
            data[a['id']] = {
                'error': e.__class__.__name__,
                'message': str(e),
            }


def render(request):
    return achilles_data(request, 'actions', [])
