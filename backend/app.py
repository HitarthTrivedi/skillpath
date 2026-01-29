from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, StudentProfile, GrowthPath, ProgressTracker, ProfessionalProfile, SimulatedTrend
from gemini_service import GeminiService
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///student_planner.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize extensions
CORS(app)
db.init_app(app)

# Initialize Gemini service
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    print("WARNING: GEMINI_API_KEY not found in environment variables")
    gemini_service = None
else:
    gemini_service = GeminiService(gemini_api_key)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_user_context(user_id):
    """Get user context for AI generation"""
    user = User.query.get(user_id)
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    completed = ProgressTracker.query.filter_by(
        user_id=user_id,
        status='completed'
    ).all()

    recent_achievements = [p.item_name for p in completed[-5:]] if completed else []

    # Extract skills from completed items
    all_skills = set()
    for item in completed:
        if item.item_type == 'project' or item.item_type == 'course':
            # You could store skills in notes or parse from item data
            pass

    analysis = profile.get_analysis() if profile else {}
    career_goal = analysis.get('career_paths', ['Professional'])[0] if analysis else 'Professional'

    return {
        'completed_count': len(completed),
        'current_phase': 1,  # Could be calculated from progress
        'career_goal': career_goal,
        'recent_achievements': recent_achievements,
        'new_skills': profile.get_skills() if profile else []
    }


# ============================================================================
# USER & ONBOARDING ENDPOINTS
# ============================================================================

@app.route('/api/v1/users/register', methods=['POST'])
def register_user():
    """Register a new user"""
    data = request.json

    if not data.get('email') or not data.get('name'):
        return jsonify({'error': 'Email and name are required'}), 400

    # Check if user exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 409

    # Create new user
    user = User(
        email=data['email'],
        name=data['name']
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201


@app.route('/api/v1/users/onboard', methods=['POST'])
def onboard_user():
    """Complete user onboarding with profile data"""
    data = request.json

    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Create or update student profile
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = StudentProfile(user_id=user_id)

    profile.major = data.get('major')
    profile.gpa = data.get('gpa')
    profile.career_aspirations = data.get('career_aspirations')
    profile.set_skills(data.get('current_skills', []))
    profile.preferred_learning = data.get('preferred_learning')
    profile.time_commitment = data.get('time_commitment')

    # Analyze profile with Gemini
    if gemini_service:
        try:
            analysis = gemini_service.analyze_student_profile({
                'major': profile.major,
                'gpa': profile.gpa,
                'career_aspirations': profile.career_aspirations,
                'current_skills': profile.get_skills(),
                'preferred_learning': profile.preferred_learning,
                'time_commitment': profile.time_commitment
            })
            profile.set_analysis(analysis)
        except Exception as e:
            print(f"Error analyzing profile: {e}")
            profile.set_analysis({
                'strengths': ['Motivated learner'],
                'gaps': ['Need more experience'],
                'career_paths': ['Professional'],
                'learning_tips': ['Start with basics']
            })

    user.onboarding_complete = True

    db.session.add(profile)
    db.session.commit()

    return jsonify({
        'message': 'Onboarding completed successfully',
        'profile': profile.to_dict()
    }), 200


@app.route('/api/v1/users/<int:user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    """Get user profile"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    profile = StudentProfile.query.filter_by(user_id=user_id).first()

    return jsonify({
        'user': user.to_dict(),
        'profile': profile.to_dict() if profile else None
    }), 200


# ============================================================================
# GROWTH PATH ENDPOINTS
# ============================================================================

@app.route('/api/v1/growth-path/generate', methods=['POST'])
def generate_growth_path():
    """Generate initial growth path roadmap"""
    data = request.json
    user_id = data.get('user_id')
    timeline_months = data.get('timeline_months', 12)

    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    user = User.query.get(user_id)
    profile = StudentProfile.query.filter_by(user_id=user_id).first()

    if not user or not profile:
        return jsonify({'error': 'User or profile not found'}), 404

    if not gemini_service:
        return jsonify({'error': 'Gemini service not available'}), 503

    try:
        # Generate roadmap with Gemini
        roadmap = gemini_service.generate_growth_path(
            profile_data={
                'major': profile.major,
                'career_aspirations': profile.career_aspirations,
                'current_skills': profile.get_skills(),
                'time_commitment': profile.time_commitment
            },
            analysis=profile.get_analysis(),
            timeline_months=timeline_months
        )

        # Save growth path
        growth_path = GrowthPath(
            user_id=user_id,
            phase=1,
            is_active=True
        )
        growth_path.set_roadmap(roadmap)

        db.session.add(growth_path)
        db.session.commit()

        # Initialize progress trackers for all items
        for phase in roadmap.get('phases', []):
            # Add courses
            for course in phase.get('courses', []):
                tracker = ProgressTracker(
                    user_id=user_id,
                    item_id=course['id'],
                    item_type='course',
                    item_name=course['name'],
                    status='not_started'
                )
                db.session.add(tracker)

            # Add tests
            for test in phase.get('tests', []):
                tracker = ProgressTracker(
                    user_id=user_id,
                    item_id=test['id'],
                    item_type='test',
                    item_name=test['name'],
                    status='not_started'
                )
                db.session.add(tracker)

            # Add internships
            for internship in phase.get('internships', []):
                tracker = ProgressTracker(
                    user_id=user_id,
                    item_id=internship['id'],
                    item_type='internship',
                    item_name=internship['type'],
                    status='not_started'
                )
                db.session.add(tracker)

            # Add certificates
            for cert in phase.get('certificates', []):
                tracker = ProgressTracker(
                    user_id=user_id,
                    item_id=cert['id'],
                    item_type='certificate',
                    item_name=cert['name'],
                    status='not_started'
                )
                db.session.add(tracker)

            # Add projects
            for project in phase.get('projects', []):
                tracker = ProgressTracker(
                    user_id=user_id,
                    item_id=project['id'],
                    item_type='project',
                    item_name=project['name'],
                    status='not_started'
                )
                db.session.add(tracker)

        db.session.commit()

        return jsonify({
            'message': 'Growth path generated successfully',
            'growth_path': growth_path.to_dict()
        }), 201

    except Exception as e:
        print(f"Error generating growth path: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/growth-path/<int:user_id>', methods=['GET'])
def get_growth_path(user_id):
    """Get current active growth path"""
    growth_path = GrowthPath.query.filter_by(
        user_id=user_id,
        is_active=True
    ).first()

    if not growth_path:
        return jsonify({'error': 'No active growth path found'}), 404

    # Get progress for all items
    progress_items = ProgressTracker.query.filter_by(user_id=user_id).all()
    progress_dict = {p.item_id: p.to_dict() for p in progress_items}

    roadmap = growth_path.get_roadmap()

    # Enrich roadmap with progress data
    for phase in roadmap.get('phases', []):
        for category in ['courses', 'tests', 'internships', 'certificates', 'projects']:
            for item in phase.get(category, []):
                item_id = item['id']
                item['progress'] = progress_dict.get(item_id, {'status': 'not_started'})

    return jsonify({
        'growth_path': growth_path.to_dict(),
        'enriched_roadmap': roadmap
    }), 200


# ============================================================================
# PROGRESS TRACKING ENDPOINTS
# ============================================================================

@app.route('/api/v1/progress/update', methods=['POST'])
def update_progress():
    """Update progress on a task"""
    data = request.json

    user_id = data.get('user_id')
    item_id = data.get('item_id')
    status = data.get('status')
    notes = data.get('notes', '')

    if not all([user_id, item_id, status]):
        return jsonify({'error': 'user_id, item_id, and status are required'}), 400

    # Find progress tracker
    tracker = ProgressTracker.query.filter_by(
        user_id=user_id,
        item_id=item_id
    ).first()

    if not tracker:
        return jsonify({'error': 'Progress tracker not found'}), 404

    tracker.status = status
    tracker.notes = notes

    # Generate encouragement if completed
    if status == 'completed' and gemini_service:
        tracker.completion_date = datetime.utcnow()

        try:
            user_context = get_user_context(user_id)
            encouragement = gemini_service.generate_encouragement(
                completed_item={
                    'item_name': tracker.item_name,
                    'item_type': tracker.item_type
                },
                user_context=user_context
            )
            tracker.encouragement_message = encouragement
        except Exception as e:
            print(f"Error generating encouragement: {e}")
            tracker.encouragement_message = f"Great job completing {tracker.item_name}!"

    db.session.commit()

    # Trigger profile update if completed
    if status == 'completed':
        try:
            update_professional_profile(user_id, tracker)
        except Exception as e:
            print(f"Error updating professional profile: {e}")

    return jsonify({
        'message': 'Progress updated successfully',
        'progress': tracker.to_dict()
    }), 200


@app.route('/api/v1/progress/<int:user_id>/summary', methods=['GET'])
def get_progress_summary(user_id):
    """Get progress summary"""
    all_items = ProgressTracker.query.filter_by(user_id=user_id).all()

    summary = {
        'total': len(all_items),
        'not_started': len([i for i in all_items if i.status == 'not_started']),
        'in_progress': len([i for i in all_items if i.status == 'in_progress']),
        'completed': len([i for i in all_items if i.status == 'completed']),
        'by_type': {}
    }

    # Group by type
    for item_type in ['course', 'test', 'internship', 'certificate', 'project']:
        type_items = [i for i in all_items if i.item_type == item_type]
        summary['by_type'][item_type] = {
            'total': len(type_items),
            'completed': len([i for i in type_items if i.status == 'completed'])
        }

    return jsonify(summary), 200


@app.route('/api/v1/progress/<int:user_id>/tasks', methods=['GET'])
def get_all_tasks(user_id):
    """Get all tasks with their progress"""
    tasks = ProgressTracker.query.filter_by(user_id=user_id).all()

    return jsonify({
        'tasks': [task.to_dict() for task in tasks]
    }), 200


# ============================================================================
# PROFESSIONAL PROFILE ENDPOINTS
# ============================================================================

def update_professional_profile(user_id, completed_item):
    """Background function to update professional profile"""
    if not gemini_service:
        return

    profile_entry = ProfessionalProfile.query.filter_by(user_id=user_id).first()
    if not profile_entry:
        profile_entry = ProfessionalProfile(user_id=user_id)
        db.session.add(profile_entry)

    current_resume = profile_entry.get_resume()

    # Generate resume bullets for completed item
    user_profile = StudentProfile.query.filter_by(user_id=user_id).first()
    analysis = user_profile.get_analysis() if user_profile else {}
    target_role = analysis.get('career_paths', ['Professional'])[0]

    try:
        bullets = gemini_service.generate_resume_bullets({
            'item_type': completed_item.item_type,
            'title': completed_item.item_name,
            'description': completed_item.notes or '',
            'skills': user_profile.get_skills() if user_profile else [],
            'target_role': target_role
        })

        # Update resume
        if completed_item.item_type == 'project':
            if 'projects' not in current_resume:
                current_resume['projects'] = []
            current_resume['projects'].append({
                'name': completed_item.item_name,
                'bullets': bullets,
                'date': completed_item.completion_date.strftime('%B %Y') if completed_item.completion_date else 'Recent'
            })

        elif completed_item.item_type == 'internship':
            if 'experience' not in current_resume:
                current_resume['experience'] = []
            current_resume['experience'].append({
                'title': completed_item.item_name,
                'bullets': bullets,
                'date': completed_item.completion_date.strftime('%B %Y') if completed_item.completion_date else 'Recent'
            })

        elif completed_item.item_type == 'certificate':
            if 'certifications' not in current_resume:
                current_resume['certifications'] = []
            current_resume['certifications'].append({
                'name': completed_item.item_name,
                'date': completed_item.completion_date.strftime('%B %Y') if completed_item.completion_date else 'Recent'
            })

        profile_entry.set_resume(current_resume)
        profile_entry.last_generated = datetime.utcnow()
        db.session.commit()

    except Exception as e:
        print(f"Error updating resume: {e}")


@app.route('/api/v1/profile/<int:user_id>/resume', methods=['GET'])
def get_resume(user_id):
    """Get auto-generated resume"""
    profile = ProfessionalProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({
            'resume': {
                'projects': [],
                'experience': [],
                'certifications': [],
                'skills': []
            }
        }), 200

    return jsonify({
        'resume': profile.get_resume(),
        'last_generated': profile.last_generated.isoformat()
    }), 200


@app.route('/api/v1/profile/<int:user_id>/linkedin', methods=['GET'])
def get_linkedin_suggestions(user_id):
    """Get LinkedIn suggestions"""
    profile = ProfessionalProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        # Generate fresh suggestions
        if gemini_service:
            try:
                user_context = get_user_context(user_id)
                linkedin_content = gemini_service.generate_linkedin_content(user_context)

                # Save suggestions
                profile = ProfessionalProfile(user_id=user_id)
                profile.set_linkedin(linkedin_content)
                db.session.add(profile)
                db.session.commit()

                return jsonify(linkedin_content), 200
            except Exception as e:
                print(f"Error generating LinkedIn content: {e}")

        return jsonify({
            'post_ideas': [],
            'profile_summary': '',
            'skills_to_add': []
        }), 200

    return jsonify(profile.get_linkedin()), 200


@app.route('/api/v1/profile/refresh', methods=['POST'])
def refresh_profile():
    """Regenerate professional profiles"""
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    if not gemini_service:
        return jsonify({'error': 'Gemini service not available'}), 503

    try:
        user_context = get_user_context(user_id)
        linkedin_content = gemini_service.generate_linkedin_content(user_context)

        profile = ProfessionalProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = ProfessionalProfile(user_id=user_id)
            db.session.add(profile)

        profile.set_linkedin(linkedin_content)
        profile.last_generated = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Profile refreshed successfully',
            'profile': profile.to_dict()
        }), 200

    except Exception as e:
        print(f"Error refreshing profile: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ADMIN/UTILITY ENDPOINTS
# ============================================================================

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'gemini_available': gemini_service is not None,
        'database': 'connected'
    }), 200


@app.route('/api/v1/trends/simulate', methods=['POST'])
def simulate_trends():
    """Simulate industry trends (hackathon helper)"""
    data = request.json
    industry = data.get('industry', 'Technology')

    # Simple trend simulation
    trend_data = {
        'hot_skills': ['AI/ML', 'Cloud Computing', 'Data Analysis', 'Cybersecurity'],
        'emerging_roles': ['ML Engineer', 'Data Scientist', 'Cloud Architect'],
        'certifications': ['AWS Certified', 'Google Cloud', 'Azure Fundamentals'],
        'industry_growth': '15% YoY'
    }

    trend = SimulatedTrend(industry=industry)
    trend.set_trends(trend_data)

    db.session.add(trend)
    db.session.commit()

    return jsonify({
        'message': 'Trends simulated',
        'trend': trend.to_dict()
    }), 201


# ============================================================================
# INITIALIZE DATABASE
# ============================================================================

@app.before_request
def initialize_database():
    """Create database tables if they don't exist"""
    if not hasattr(app, 'db_initialized'):
        with app.app_context():
            db.create_all()
        app.db_initialized = True


# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, host='0.0.0.0', port=5000)