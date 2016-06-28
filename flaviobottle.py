import flavio
from bottle import hook, response, route, run, request, default_app
import math
import json

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
            'arguments': obs.arguments,
            }

def pretty_prediction(cen, unc=None):
    if unc is None:
        sig = 3
    else:
        sig = max(0, math.floor(math.log10(abs(cen/unc))) + 2)
    if cen == 0:
        exponent = 0
    else:
        exponent = math.floor(math.log10(abs(cen)))
    if exponent == 1 or exponent == -1:
        exponent = 0
    if unc is not None:
        if math.floor(math.log10(abs(unc))) > exponent:
            exponent = math.floor(math.log10(abs(unc)))
    cen_sc = cen/10.**exponent
    if abs(exponent) > 1:
        exponent_string = ' × 10<sup>' +  str(exponent).replace('-', '−') + '</sup>'
    else:
        exponent_string = ''
    format_cen = '{:.' + str(sig) + '}'
    format_unc = '{:.2}'
    central_string = format_cen.format(cen_sc)
    if unc is None:
        return central_string + exponent_string
    else:
        unc_sc = unc/10.**exponent
        unc_string = format_unc.format(unc_sc)
        return '(' + central_string + ' ± '+ unc_string + ' )' + exponent_string


@route('/prediction')
def prediction():
    try:
        obsname = request.query.obs
        obs = flavio.Observable.get_instance(obsname)
        if obs.arguments is not None:
            args = json.loads(request.query.args)
            # transform strings of numbers to numbers
            def tofloat(s):
                try:
                    f = float(s)
                except:
                    return s
                return f
            args = {key: tofloat(val) for key, val in args.items()}
    except:
        return {}
    if obs.arguments is None:
        cen = flavio.sm_prediction(obsname)
    else:
        cen = flavio.sm_prediction(obsname, **args)
    if request.query.unc == 'true':
        if obs.arguments is None:
                unc = flavio.sm_uncertainty(obsname)
        else:
                unc = flavio.sm_uncertainty(obsname, **args)
        return {'prediction': pretty_prediction(cen, unc), 'central': cen, 'uncertainty': unc}
    else:
        return {'prediction': pretty_prediction(cen), 'central': cen}

application = default_app()
