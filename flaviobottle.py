import flavio
from bottle import hook, response, route, run, request, default_app

@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'

@route('/')
def hello_world():
    return "Hello from Flavio's Bottle!"

@route('/obslist')
def obslist():
    allobs = list(flavio.Observable.instances.keys())
    return {'obslist':allobs}

@route('/observable')
def observable():
    try:
        obs = flavio.Observable.get_instance(request.query.name)
    except:
        return {}
    return {
            'name': obs.name,
            'tex': obs.tex,
            'description': obs.description,
            }

application = default_app()
