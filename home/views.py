from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from rest_framework.decorators import api_view
import pandas as pd
import requests
from django.views.decorators.csrf import csrf_exempt


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
        print(request.POST)
        user_preferences = {key: float(value) for key, value in user_preferences.items()}
        
        
        def calculate_search_score(course, preferences):
            course_words = course.lower().split()
            preference_words = [word.lower() for preference in preferences for word in preference.split()]
            
            # Initialize a list to store scores for partial matches
            partial_match_scores = []
            
            # Iterate through each preference word
            for preference_word in preference_words:
                # Check if the preference word partially matches any word in the course description
                for course_word in course_words:
                    if preference_word in course_word:
                        # Calculate the percentage of matching characters
                        match_percentage = len(preference_word) / len(course_word) * 100
                        partial_match_scores.append(match_percentage)
                        break  # Break once a match is found for the preference word
            
            # If there are partial match scores, take the maximum score
            if partial_match_scores:
                score = max(partial_match_scores)
            else:
                score = 0
            
            return score




        df['search_score'] = df['course'].apply(calculate_search_score, preferences=user_preferences)
        filtered_df = df[df['search_score'] > 0]
        result_df = filtered_df[['course', 'final_score', 'search_score']]
        sorted_result_df = result_df.sort_values(by='final_score', ascending=False)
        json_data = sorted_result_df.to_json(orient='records')
        return HttpResponse(json_data, content_type='application/json')
    redirect('/')


@csrf_exempt
def analytics(request):
    redirect('/')