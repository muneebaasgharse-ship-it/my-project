# recommendations.py - Complete file (copy everything)
import pandas as pd
import numpy as np

def get_factor_analysis(student_data, feature_importance):
    """
    Analyze which factors are hurting the student's performance
    Returns list of weak areas with detailed info
    """
    
    weak_areas = []
    
    # Check Attendance
    attendance = student_data.get('Attendance', 100)
    if attendance < 75:
        weak_areas.append({
            'factor': 'Low Attendance',
            'severity': 'High',
            'current': f"{attendance}%",
            'target': '75%+',
            'impact': 'Directly reduces final exam score by 15-20 points',
            'actions': [
                'Set daily reminders for class timings',
                'Get notes from classmates for missed classes',
                'Meet with teacher to catch up on missed content',
                'Aim for 90%+ attendance next month'
            ]
        })
    elif attendance < 85:
        weak_areas.append({
            'factor': 'Moderate Attendance',
            'severity': 'Medium',
            'current': f"{attendance}%",
            'target': '85%+',
            'impact': 'Improving attendance will boost performance',
            'actions': [
                'Try not to miss more than 1 class per week',
                'Plan appointments outside class hours',
                'Inform teacher in advance if you must miss'
            ]
        })
    
    # Check Study Hours
    study_hours = student_data.get('Study Hours', 0)
    if study_hours < 4:
        weak_areas.append({
            'factor': 'Insufficient Study Hours',
            'severity': 'High',
            'current': f"{study_hours} hrs/week",
            'target': '8+ hrs/week',
            'impact': 'Strong correlation with exam performance',
            'actions': [
                'Create a weekly study schedule (2 hours daily)',
                'Use active recall and practice testing',
                'Study in focused 45-minute blocks with breaks',
                'Join library study sessions for better focus'
            ]
        })
    elif study_hours < 6:
        weak_areas.append({
            'factor': 'Moderate Study Hours',
            'severity': 'Medium',
            'current': f"{study_hours} hrs/week",
            'target': '8+ hrs/week',
            'impact': 'Increasing study time can improve grades',
            'actions': [
                'Add 1-2 extra study hours per week',
                'Use weekends for revision',
                'Study with focused goals each session'
            ]
        })
    
    # Check Assignment Scores
    avg_assignments = (student_data.get('Assignment1', 0) + student_data.get('Assignment2', 0)) / 2
    if avg_assignments < 60:
        weak_areas.append({
            'factor': 'Low Assignment Scores',
            'severity': 'Medium',
            'current': f"{avg_assignments:.1f}",
            'target': '75+',
            'impact': 'Assignments build foundation for exams',
            'actions': [
                'Start assignments at least 5 days before deadline',
                'Review assignment rubric before starting',
                'Ask teacher for sample high-scoring assignments',
                'Get peer feedback before submission'
            ]
        })
    
    # Check Test Scores
    avg_tests = (student_data.get('Test1', 0) + student_data.get('Test2', 0)) / 2
    if avg_tests < 55:
        weak_areas.append({
            'factor': 'Poor Test Performance',
            'severity': 'High',
            'current': f"{avg_tests:.1f}",
            'target': '65+',
            'impact': 'Indicates weak concept understanding',
            'actions': [
                'Solve past exam papers (at least 5)',
                'Create concept summaries for each chapter',
                'Form a study group for test preparation',
                'Meet teacher for doubt clarification sessions'
            ]
        })
    elif avg_tests < 70:
        weak_areas.append({
            'factor': 'Average Test Performance',
            'severity': 'Low',
            'current': f"{avg_tests:.1f}",
            'target': '70+',
            'impact': 'Good but can be better',
            'actions': [
                'Review mistakes from previous tests',
                'Practice more numerical problems',
                'Focus on time management during exams'
            ]
        })
    
    # Check Previous GPA
    previous_gpa = student_data.get('Previous_GPA', 3.0)
    if previous_gpa < 2.5:
        weak_areas.append({
            'factor': 'Low Previous GPA',
            'severity': 'Medium',
            'current': f"{previous_gpa}",
            'target': '2.8+',
            'impact': 'Historical struggle in academics',
            'actions': [
                'Meet with academic advisor',
                'Develop better study strategies',
                'Focus on foundational concepts'
            ]
        })
    
    # Check Participation
    participation = student_data.get('Participation', 0)
    if participation < 50:
        weak_areas.append({
            'factor': 'Low Class Participation',
            'severity': 'Low',
            'current': f"{participation}",
            'target': '70+',
            'impact': 'Active participation improves understanding',
            'actions': [
                'Prepare questions before class',
                'Try to answer at least 1 question per class',
                'Join class discussions actively'
            ]
        })
    
    # Check Project Score
    project_score = student_data.get('Project_Score', 0)
    if project_score < 60:
        weak_areas.append({
            'factor': 'Low Project Score',
            'severity': 'Medium',
            'current': f"{project_score}",
            'target': '75+',
            'impact': 'Projects carry significant weight',
            'actions': [
                'Start projects early',
                'Regularly consult with teacher',
                'Work with stronger teammates',
                'Follow project rubric closely'
            ]
        })
    
    return weak_areas

def generate_actionable_recommendations(weak_areas, predicted_category):
    """Generate specific recommendations based on weak areas"""
    
    recommendations = []
    
    # General recommendation based on prediction
    if predicted_category == 'At-Risk':
        recommendations.append({
            'priority': 'CRITICAL',
            'title': '🚨 Immediate Intervention Required',
            'category': 'General',
            'actions': [
                'Schedule meeting with academic advisor THIS WEEK',
                'Attend all remaining classes without fail',
                'Request extra tutoring sessions',
                'Submit all pending assignments immediately',
                'Create a daily study plan and stick to it'
            ]
        })
    elif predicted_category == 'Average':
        recommendations.append({
            'priority': 'HIGH',
            'title': '📈 Improvement Plan Needed',
            'category': 'General',
            'actions': [
                'Increase study hours by 2-3 hours per week',
                'Form a study group with better-performing students',
                'Complete all practice problems before exams',
                'Review test mistakes thoroughly',
                'Set weekly academic goals'
            ]
        })
    else:  # Good
        recommendations.append({
            'priority': 'LOW',
            'title': '🌟 Maintain Excellence',
            'category': 'General',
            'actions': [
                'Keep up current study habits',
                'Help struggling classmates (teaching reinforces learning)',
                'Explore advanced topics beyond syllabus',
                'Maintain consistent attendance'
            ]
        })
    
    # Specific recommendations for each weak area
    for area in weak_areas:
        recommendations.append({
            'priority': area['severity'].upper(),
            'title': f"📚 {area['factor']}",
            'category': 'Specific',
            'actions': area.get('actions', [
                f"Improve {area['factor']} from {area['current']} to {area['target']}",
                "Track progress weekly",
                "Seek help from teacher"
            ])
        })
    
    return recommendations

def generate_early_alert(student_data, predicted_category, weak_areas):
    """Generate early alert message for at-risk students"""
    
    final_score = student_data.get('Final Exam', 0)
    
    if predicted_category == 'At-Risk':
        alert_level = '🔴 CRITICAL ALERT'
        alert_color = '#ffcccc'
        message = f"⚠️ HIGH RISK: Student is at serious risk of failing"
        
        details = [
            f"📊 Current Final Exam Score: {final_score}/100",
            f"📅 Attendance: {student_data.get('Attendance', 'N/A')}%",
            f"⏰ Study Hours: {student_data.get('Study Hours', 'N/A')} hrs/week",
            f"📝 Assignment Avg: {(student_data.get('Assignment1',0) + student_data.get('Assignment2',0))/2:.1f}",
            f"📋 Test Avg: {(student_data.get('Test1',0) + student_data.get('Test2',0))/2:.1f}"
        ]
        
        recommendation = "Immediate intervention required. Contact parents and schedule tutoring."
        
    elif predicted_category == 'Average' and len(weak_areas) >= 2:
        alert_level = '🟡 WARNING'
        alert_color = '#fff3cc'
        message = f"⚠️ Warning: Student needs improvement in {len(weak_areas)} areas"
        
        details = [f"⚠️ Areas needing attention: {', '.join([w['factor'] for w in weak_areas[:3]])}"]
        
        recommendation = "Monitor progress closely. Implement improvement plan."
        
    else:
        alert_level = '🟢 ON TRACK'
        alert_color = '#ccffcc'
        message = f"✅ Student is performing adequately"
        
        details = [
            "✓ Maintain current study habits",
            "✓ Focus on consistent attendance",
            "✓ Keep up with assignments"
        ]
        
        recommendation = "Continue current strategies. Regular check-ins recommended."
    
    return {
        'level': alert_level,
        'color': alert_color,
        'message': message,
        'details': details,
        'recommendation': recommendation
    }

def get_performance_factors(student_data, feature_importance):
    """Identify which factors are helping or hurting the student"""
    
    helping_factors = []
    hurting_factors = []
    
    # Check attendance
    if student_data.get('Attendance', 0) >= 85:
        helping_factors.append("Excellent attendance record")
    elif student_data.get('Attendance', 0) < 70:
        hurting_factors.append("Low attendance affecting performance")
    
    # Check study hours
    if student_data.get('Study Hours', 0) >= 8:
        helping_factors.append("Good study habits (8+ hours/week)")
    elif student_data.get('Study Hours', 0) < 4:
        hurting_factors.append("Insufficient study time")
    
    # Check assignments
    avg_assign = (student_data.get('Assignment1', 0) + student_data.get('Assignment2', 0)) / 2
    if avg_assign >= 80:
        helping_factors.append("Strong assignment performance")
    elif avg_assign < 60:
        hurting_factors.append("Low assignment scores")
    
    # Check tests
    avg_test = (student_data.get('Test1', 0) + student_data.get('Test2', 0)) / 2
    if avg_test >= 75:
        helping_factors.append("Good test performance")
    elif avg_test < 55:
        hurting_factors.append("Poor test performance")
    
    # Check previous GPA
    if student_data.get('Previous_GPA', 0) >= 3.5:
        helping_factors.append("Strong academic history")
    elif student_data.get('Previous_GPA', 0) < 2.5:
        hurting_factors.append("Low previous GPA")
    
    return helping_factors, hurting_factors