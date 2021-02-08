from ..version import __version__


def setup(app):
    print(app)

    return {
        'version': __version__
    }
