from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View

from core.StreamingApp.form import AddProducerForm, AddStudioForm
from .models import Producer, Studio

# @login_required
class AdminHomepageView(View):
    def get(self,request):
        return render(request, 'admin/admin_homepage.html')
    
class AddProducerView(View):
    def get(self, request):
        # Provide an empty form instance so template can render it
        add_producer_form = AddProducerForm()
        return render(request, 'admin/add_producer.html', {
            'add_producer_form': add_producer_form,
        })

    def post(self, request):
        add_producer_form = AddProducerForm(request.POST)
        if add_producer_form.is_valid():
            add_producer_form.save()
            return redirect('manage_producer')
        # Re-render with bound form to show validation errors
        return render(request, 'admin/add_producer.html', {
            'add_producer_form': add_producer_form,
        })


class AddStudioView(View):
    def get(self, request):
        add_studio_form = AddStudioForm()
        return render(request, 'admin/add_studio.html', {
            'add_studio_form': add_studio_form
        })
    
    def post(self,request):
        add_studio_form = AddStudioForm(request.POST)
        if add_studio_form.is_valid():
            add_studio_form.save()
            return redirect('manage_producer')
        return render(request, 'admin/add_studio.html', {
            'add_studio_form' : add_studio_form
        })

class ManageProducerView(View):
    def get(self,request):
        producers = Producer.objects.all()
        return render(request, 'admin/manage_producer.html', {
            'producers': producers,
        })

class ManageStudioView(View):
    def get(self,request):
        studios = Studio.objects.all()
        return render(request, 'admin/manage_studio.html', {
            'studios' : studios
        })

class EditProducerView(View):
    def get(self,request, producer_id):
        producer = get_object_or_404(Producer, producer_id=producer_id)
        edit_producer_form = AddProducerForm(instance=producer)
        return render(request, 'admin/edit_producer.html', {
            'edit_producer_form': edit_producer_form,
        })
    
    def post(self,request, producer_id):
        producer = get_object_or_404(Producer, producer_id= producer_id)
        edit_producer_form = AddProducerForm(request.POST, instance= producer)
        if edit_producer_form.is_valid():
            edit_producer_form.save()
            return redirect('manage_producer')
        return render(request, 'admin/edit_producer.html',{
            'edit_producer_form' : edit_producer_form
        })

class EditStudioView(View):
    def get(self,request, studio_id):
        studio = get_object_or_404(Studio, studio_id=studio_id)
        edit_studio_form = AddStudioForm(instance=studio)
        return render(request, 'admin/edit_studio.html', {
            'edit_studio_form': edit_studio_form,
        })
    
    def post(self, request, studio_id):
        studio= get_object_or_404(Studio, studio_id=studio_id)
        edit_studio_form = AddStudioForm(request.POST, instance=studio)
        if edit_studio_form.is_valid():
            edit_studio_form.save()
            return redirect('manage_studio')
        return render(request, 'admin/edit_studio.html', {
            'edit_studio_form': edit_studio_form,
        })

    
    def post(self,request, studio_id):
        studio = get_object_or_404(Studio, studio_id= studio_id)
        edit_studio_form = AddStudioForm(request.POST, instance= studio)
        if edit_studio_form.is_valid():
            edit_studio_form.save()
            return redirect('manage_studio')
        render(request, 'admin/edit_studio.html',{
            'edit_studio_form' : edit_studio_form
        })

admin_homepage = AdminHomepageView.as_view()
add_producer = AddProducerView.as_view()
add_studio = AddStudioView.as_view()
manage_producer = ManageProducerView.as_view()
manage_studio = ManageStudioView.as_view()
edit_producer = EditProducerView.as_view()
# add_film = AddFilmView.as_view()
