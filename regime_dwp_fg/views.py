from django.shortcuts import render
from django.urls import reverse
from core_home.views import start_url

def start(request):
    select_dict = request.session.get('select_dict')
    regime_id = select_dict['regime_id']
    regime_name = select_dict['regime_name']

    home_html = 'regime_' + regime_id.lower() + '/home.html'
    continue_html=start_url(request)
    print('The home page for ', regime_name, ' will send user to ', continue_html, ' for data entry')

    return render(request, home_html, {'regime_name': regime_name, 'continue_html': continue_html})



