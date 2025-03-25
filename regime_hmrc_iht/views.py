from django.shortcuts import render

def start(request):

    regime_id = request.session.get('select_dict', {}).get('regime_id')
    regime_name = request.session.get("select_dict", {}).get("regime_name")
    home_html = 'regime_' + regime_id.lower() + '/home.html'
    return render(request, home_html,{'regime_name': regime_name})

