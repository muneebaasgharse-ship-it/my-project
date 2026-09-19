# utils.py
import pandas as pd
import numpy as np

def calculate_risk_level(score):
    """Calculate risk level based on final exam score"""
    if score < 35:
        return "High Risk", "🔴"
    elif score < 50:
        return "Moderate Risk", "🟡"
    elif score < 70:
        return "Low Risk", "🟢"
    else:
        return "Excellent", "🌟"

def get_performance_category(score):
    """Get performance category"""
    if score < 35:
        return "At-Risk"
    elif score < 50:
        return "Below Average"
    elif score < 70:
        return "Average"
    else:
        return "Excellent"

def calculate_class_statistics(df, course=None):
    """Calculate class statistics"""
    if course and course != 'All':
        filtered_df = df[df['Course'] == course]
    else:
        filtered_df = df
    
    stats = {
        'total_students': len(filtered_df),
        'avg_attendance': filtered_df['Attendance'].mean(),
        'avg_final_exam': filtered_df['Final Exam'].mean(),
        'avg_study_hours': filtered_df['Study Hours'].mean(),
        'at_risk_count': len(filtered_df[filtered_df['Final Exam'] < 35]),
        'excellent_count': len(filtered_df[filtered_df['Final Exam'] >= 70])
    }
    return stats

def generate_recommendations(student_data):
    """Generate personalized recommendations"""
    recommendations = []
    
    # Attendance recommendations
    if student_data['Attendance'] < 75:
        recommendations.append({
            'area': 'Attendance',
            'priority': 'High',
            'message': 'Your attendance is below 75%. This puts you at risk.',
            'actions': [
                'Attend all classes regularly',
                'Meet with teachers to catch up',
                'Set attendance reminders'
            ]
        })
    elif student_data['Attendance'] < 85:
        recommendations.append({
            'area': 'Attendance',
            'priority': 'Medium',
            'message': 'Your attendance is good but can be improved.',
            'actions': [
                'Try to maintain attendance above 85%',
                'Plan your schedule to avoid conflicts'
            ]
        })
    
    # Study hours recommendations
    if student_data['Study Hours'] < 4:
        recommendations.append({
            'area': 'Study Habits',
            'priority': 'High',
            'message': 'You need to increase your study hours.',
            'actions': [
                'Create a daily study schedule',
                'Join study groups',
                'Use active learning techniques'
            ]
        })
    
    # Performance recommendations
    final_score = student_data['Final Exam']
    if final_score < 35:
        recommendations.append({
            'area': 'Academic Performance',
            'priority': 'Critical',
            'message': 'You are at risk of failing.',
            'actions': [
                'Schedule meeting with academic advisor',
                'Get extra tutoring',
                'Review all course materials',
                'Practice more problems'
            ]
        })
    elif final_score < 50:
        recommendations.append({
            'area': 'Academic Performance',
            'priority': 'High',
            'message': 'Your performance needs improvement.',
            'actions': [
                'Focus on weak areas',
                'Complete all assignments',
                'Attend extra help sessions'
            ]
        })
    
    return recommendations