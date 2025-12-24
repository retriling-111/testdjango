from django.shortcuts import render


    # ဒါဟာ Python Dictionary ပါပဲ
    # Key ("title") က HTML ထဲမှာ သုံးမယ့်နာမည်ဖြစ်ပြီး
    # Value ("Learning Django") က ပြမယ့်စာသားပါ

from .models import Profile  # အပေါ်ဆုံးမှာ ဒါပါရပါမယ်

def home(request):
    # Database ထဲက အချက်အလက်အားလုံးကို ဆွဲထုတ်မယ်
    # အကယ်၍ လူတစ်ယောက်တည်းဆိုရင် .first() နဲ့ ယူလို့ရပါတယ်
    # .first() ကို သုံးရင်တော့ Django က စာရင်းထဲက "ပထမဆုံး တစ်ယောက်တည်း" ကိုပဲ လက်ထဲထည့်ပေးလိုက်တာပါ။
    my_profile = Profile.objects.all() 
    
    context = {
        "user_data": my_profile
    }
    return render(request, 'home.html', context)
    # render သုံးပြီး Dictionary (my_data) ကို HTML ဆီ ပို့လိုက်တာပါ
    # return render(request, 'home.html', my_data)
    
def profile_detail(request, pk): # pk ဆိုတာ primary key (id) ပါ
    profile = Profile.objects.get(id=pk)
    return render(request, 'detail.html', {'profile': profile})


from .forms import ProfileForm
from django.shortcuts import redirect

def add_profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES) # ပုံပါရင် request.FILES လိုပါတယ်
        if form.is_valid():
            form.save() # ဒါက database ထဲကို တန်းပို့ပေးတာပါ
            return redirect('home') # ပြီးရင် home page ကို ပြန်သွားမယ်
    else:
        form = ProfileForm()
    return render(request, 'add_profile.html', {'form': form})

