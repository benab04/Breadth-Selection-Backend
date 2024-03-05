from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from rest_framework.decorators import api_view
import pandas as pd
import requests
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import *

def dashboard(request):
    final_grades_path = 'data/final_grades.csv'
    df = pd.read_csv(final_grades_path)
    course_data = df
    user_preferences = {'Aerodynamics': 0.8, 'Mathematics': 0.9, 'Language': 0.9}

    def calculate_score(course, preferences):
        score = 0
        for pref, weight in preferences.items():
            if pref.lower() in course.lower():
                score += weight
        return score

    course_data['Score'] = course_data['course'].apply(calculate_score, preferences=user_preferences)
    total_students = course_data[['EX', 'A', 'B', 'C', 'D', 'P', 'F']].sum(axis=1)
    grade_distribution = course_data[['EX', 'A', 'B', 'C', 'D', 'P', 'F']].div(total_students, axis=0)
    course_data['Avg_Score'] = grade_distribution[['EX', 'A', 'B', 'C', 'D']].dot([0.9, 0.8, 0.7, 0.6, 0.5])
    course_data['Final_Score'] = course_data['Score'] + course_data['Avg_Score']
    filtered_courses = course_data[course_data['Score'] > 0]
    sorted_courses = filtered_courses.sort_values(by='Final_Score', ascending=False)
    json_data = sorted_courses.to_json(orient='records')
    
    return HttpResponse(json_data)

@csrf_exempt
def preferences(request):
    if request.method=="POST":
        final_grades_path = 'data/newer_df.csv'
        df = pd.read_csv(final_grades_path)
        course_data = df
        user_preferences=request.POST
        
        user_preferences = {key: float(value) for key, value in user_preferences.items()}
        
        def calculate_search_score(course, preferences):
            course_words = course.lower().split()
            
            partial_match_scores = []
            
            for preference, weightage in preferences.items():
                preference_words = preference.lower().split()
                for preference_word in preference_words:
                    for course_word in course_words:
                        if preference_word in course_word:
                            match_percentage = len(preference_word) / len(course_word) * 100
                            weighted_score = match_percentage * weightage
                            partial_match_scores.append(weighted_score)
                            break 
                    else:
                        continue
                    break 
            
            if partial_match_scores:
                score = max(partial_match_scores)
            else:
                score = 0
            
            return score




        df['search_score'] = df['course'].apply(calculate_search_score, preferences=user_preferences)
        filtered_df = df[df['search_score'] > 0]
        result_df = filtered_df[['course', 'final_score', 'search_score']]
        result_df['search_score']= (result_df['search_score']/100 )*20
        result_df['final_score']= result_df['final_score']*0.6 + result_df['search_score']*0.4 

        sorted_result_df = result_df.sort_values(by='final_score', ascending=False)
        json_data = sorted_result_df.to_json(orient='records')
        return HttpResponse(json_data, content_type='application/json')
    redirect('/')


@csrf_exempt
def analytics(request):
    if request.method=="POST":
        course_name = request.POST.get("Course", None)
        all_df = pd.read_csv('data/final_grades.csv')
        sessions = all_df[all_df['course'] == course_name]
        
        def custom_sort(item):
            season, year = item.split()
            return (year, 0 if season == 'Spring' else 1)
        
        sorted_sessions = sessions.copy()
        sorted_sessions['session'] = sorted_sessions['session'].apply(custom_sort)
        sorted_sessions = sorted_sessions.sort_values(by='session')
        sorted_sessions['session'] = sorted_sessions['session'].apply(lambda x: f"{x[0]} {'Spring' if x[1] == 0 else 'Autumn'}")
        
        sorted_sessions = sorted_sessions.drop(["course"], axis=1)
        
        json_data = sorted_sessions.to_json(orient='records')
        return HttpResponse(json_data, content_type='application/json')
    redirect('/')
    
@csrf_exempt
def login_page(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        print(username, password)
        if not User.objects.filter(username=username).exists():
            return JsonResponse({"error": "User not registered"}, status=400)
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return JsonResponse({"error": "Invalid password"}, status=401)
        
        else:
            login(request, user)
            return JsonResponse({"success": "Login Successful"}, status=200)
            
    return JsonResponse({"error": "Bad Request"}, status=400)

@csrf_exempt
def register_page(request):
    if request.method=="POST":
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        username=request.POST.get('username')
        password=request.POST.get('password')
        
        user=User.objects.filter(username=username)
        
        if user.exists():
            return JsonResponse({"error": "User is already registered"}, status=400)
        
        user=User.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        
        user.set_password(password)
        user.save()
        return JsonResponse({"error": "Account created successfully"}, status=200)

    return JsonResponse({"error": "Bad Request"}, status=400)
@csrf_exempt
def logout_page(request):
    logout(request)
    return JsonResponse({"success": "Logged out"}, status=200)
