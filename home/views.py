from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from rest_framework.decorators import api_view
import pandas as pd
import requests
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
def dashboard(request):
    
    
    final_grades_path = 'data/final_grades.csv'

    df = pd.read_csv(final_grades_path)

    


    # Example DataFrame with course data
    course_data = df

    # User input preferences and corresponding weights
    user_preferences = {'Aerodynamics': 0.8, 'Mathematics': 0.9, 'Language': 0.9}

    # Function to calculate weighted score based on user preferences and grade distribution
    def calculate_score(course, preferences):
        score = 0
        for pref, weight in preferences.items():
            if pref.lower() in course.lower():
                score += weight
        return score

    # Calculate score for each course based on weighted user preferences
    course_data['Score'] = course_data['course'].apply(calculate_score, preferences=user_preferences)

    # Normalize grade distribution and calculate average score for each course
    total_students = course_data[['EX', 'A', 'B', 'C', 'D', 'P', 'F']].sum(axis=1)
    grade_distribution = course_data[['EX', 'A', 'B', 'C', 'D', 'P', 'F']].div(total_students, axis=0)
    course_data['Avg_Score'] = grade_distribution[['EX', 'A', 'B', 'C', 'D']].dot([0.9, 0.8, 0.7, 0.6, 0.5])

    # Combine weighted user preferences score and average score based on grade distribution
    course_data['Final_Score'] = course_data['Score'] + course_data['Avg_Score']

    # Filter out courses that don't have any preference keywords
    filtered_courses = course_data[course_data['Score'] > 0]

    # Sort courses by final score in descending order
    sorted_courses = filtered_courses.sort_values(by='Final_Score', ascending=False)

    # Display sorted courses
    # print(sorted_courses[['course', 'Final_Score']])

    # Example DataFrame with course data
    course_data = df

    # User input preferences
    user_preferences = ['data', 'programming']

    # Function to calculate score based on user preferences
    def calculate_score(course, preferences):
        return sum(1 for pref in preferences if pref.lower() in course.lower())

    # Calculate score for each course based on how many user preferences match the course name
    course_data['Score'] = course_data['course'].apply(calculate_score, preferences=user_preferences)

    # Filter out courses that don't have any preference keywords
    filtered_courses = course_data[course_data['Score'] > 0]

    # Sort courses by score in descending order
    sorted_courses = filtered_courses.sort_values(by='Score', ascending=False)

    # Display sorted courses
    # print(sorted_courses['course'])
    json_data = sorted_courses.to_json(orient='records')
    
    return HttpResponse(json_data)
@csrf_exempt
def preferences(request):
        if request.method=="POST":
            final_grades_path = 'data/final_grades.csv'

            df = pd.read_csv(final_grades_path)
            course_data = df
           
            # User input preferences and corresponding weights
            user_preferences=request.POST
            

            user_preferences = {key: float(value) for key, value in user_preferences.items()}
            print(user_preferences)
            # Function to calculate weighted score based on user preferences and grade distribution
            def calculate_score(course, preferences):
                score = 0
                for pref, weight in preferences.items():
                    if pref.lower() in course.lower():
                        score += weight
                return score

            # Calculate score for each course based on weighted user preferences
            course_data['Score'] = course_data['course'].apply(calculate_score, preferences=user_preferences)

            # Normalize grade distribution and calculate average score for each course
            total_students = course_data[['EX', 'A', 'B', 'C', 'D', 'P', 'F']].sum(axis=1)
            grade_distribution = course_data[['EX', 'A', 'B', 'C', 'D', 'P', 'F']].div(total_students, axis=0)
            course_data['Avg_Score'] = grade_distribution[['EX', 'A', 'B', 'C', 'D']].dot([0.9, 0.8, 0.7, 0.6, 0.5])

            # Combine weighted user preferences score and average score based on grade distribution
            course_data['Final_Score'] = course_data['Score'] + course_data['Avg_Score']

            # Filter out courses that don't have any preference keywords
            filtered_courses = course_data[course_data['Score'] > 0]

            # Sort courses by final score in descending order
            sorted_courses = filtered_courses.sort_values(by='Final_Score', ascending=False)

            # Display sorted courses
            # print(sorted_courses[['course', 'Final_Score']])
            json_data = sorted_courses.to_json(orient='records')
                
            return HttpResponse(json_data, content_type='application/json')
        redirect('/')