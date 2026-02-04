from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, StudentProfile, GrowthPath, ProgressTracker, ProfessionalProfile, SimulatedTrend
from gemini_service import GeminiService
from datetime import datetime
import os
import json
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

    recent_achievements = [
        {
            'item_name': p.item_name,
            'item_type': p.item_type,
            'completion_date': p.completion_date.isoformat() if p.completion_date else None
        }
        for p in completed[-5:]
    ] if completed else []

    analysis = profile.get_analysis() if profile else {}
    career_goal = analysis.get('career_paths', ['Professional'])[0] if analysis else 'Professional'

    return {
        'name': user.name if user else None,
        'major': profile.major if profile else None,
        'university': profile.university if profile else None,
        'experience_level': profile.experience_level if profile else None,
        'career_goal': career_goal,
        'career_aspirations': profile.career_aspirations if profile else None,
        'target_industries': profile.get_target_industries() if profile else [],
        'current_skills': profile.get_skills() if profile else [],
        'preferred_learning': profile.preferred_learning if profile else None,
        'preferred_content_types': profile.get_preferred_content_types() if profile else [],
        'time_commitment': profile.time_commitment if profile else None,
        'recent_achievements': recent_achievements,
        'new_skills': profile.get_skills() if profile else [],
        'completed_count': len(completed),
        'current_phase': 1  # could be refined later
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
    profile.university = data.get('university')
    profile.gpa = data.get('gpa')
    profile.career_aspirations = data.get('career_aspirations')
    profile.set_skills(data.get('current_skills', []))
    profile.experience_level = data.get('experience_level')
    profile.set_target_industries(data.get('target_industries', []))
    profile.preferred_learning = data.get('preferred_learning')
    profile.set_preferred_content_types(data.get('preferred_content_types', []))
    profile.time_commitment = data.get('time_commitment')
    
    # New Fields
    profile.profile_photo = data.get('profile_photo')
    profile.relocation_goal = data.get('relocation_goal')
    profile.set_extracurricular_interests(data.get('extracurricular_interests', []))
    profile.planning_horizon_years = data.get('planning_horizon_years', 1)

    # Analyze profile with Gemini
    if gemini_service:
        try:
            analysis = gemini_service.analyze_student_profile({
                'major': profile.major,
                'university': profile.university,
                'gpa': profile.gpa,
                'career_aspirations': profile.career_aspirations,
                'current_skills': profile.get_skills(),
                'experience_level': profile.experience_level,
                'target_industries': profile.get_target_industries(),
                'preferred_learning': profile.preferred_learning,
                'preferred_content_types': profile.get_preferred_content_types(),
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


@app.route('/api/v1/profile/details', methods=['POST'])
def update_profile_details():
    """Update contact and social details"""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
        
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
        
    if 'phone_number' in data:
        profile.phone_number = data['phone_number']
    if 'linkedin_url' in data:
        profile.linkedin_url = data['linkedin_url']
    if 'github_url' in data:
        profile.github_url = data['github_url']
    if 'portfolio_url' in data:
        profile.portfolio_url = data['portfolio_url']
        
    db.session.commit()
    
    return jsonify({
        'message': 'Profile details updated',
        'profile': profile.to_dict()
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
                'university': profile.university,
                'career_aspirations': profile.career_aspirations,
                'experience_level': profile.experience_level,
                'target_industries': profile.get_target_industries(),
                'current_skills': profile.get_skills(),
                'preferred_content_types': profile.get_preferred_content_types(),
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


@app.route('/api/v1/growth-path/extend', methods=['POST'])
def extend_growth_path_endpoint():
    """Extend roadmap when all tasks are completed"""
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    try:
        # Verify all tasks are completed before extending
        all_tasks = ProgressTracker.query.filter_by(user_id=user_id).all()
        completed_tasks = [t for t in all_tasks if t.status == 'completed']
        
        if len(all_tasks) == 0:
            return jsonify({'error': 'No tasks found. Please generate a roadmap first.'}), 400
        
        if len(completed_tasks) != len(all_tasks):
            return jsonify({
                'error': 'Not all tasks are completed yet',
                'completed': len(completed_tasks),
                'total': len(all_tasks)
            }), 400
        
        # Store task count before extension
        all_tasks = ProgressTracker.query.filter_by(user_id=user_id).all()
        task_count_before = len(all_tasks)
        
        result = extend_growth_path(user_id)
        
        # Verify tasks were actually created
        all_tasks_after = ProgressTracker.query.filter_by(user_id=user_id).all()
        new_task_count = len(all_tasks_after) - task_count_before
        
        if new_task_count == 0:
            print("WARNING: Extension completed but no new tasks were created!")
            return jsonify({
                'error': 'Roadmap extended but no tasks were created. Please check backend logs.',
                'new_phase': result,
                'tasks_created': 0
            }), 500
        
        return jsonify({
            'message': 'Roadmap extended successfully',
            'new_phase': result,
            'tasks_added': True,
            'tasks_created': new_task_count
        }), 201
    except Exception as e:
        print(f"Error extending roadmap: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def extend_growth_path(user_id):
    """Extend the growth path with a new phase"""
    if not gemini_service:
        raise Exception('Gemini service not available')

    user = User.query.get(user_id)
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    current_path = GrowthPath.query.filter_by(user_id=user_id, is_active=True).first()

    if not user or not profile or not current_path:
        raise Exception('User, profile, or active growth path not found')

    # Get current roadmap
    current_roadmap = current_path.get_roadmap()
    current_phases = current_roadmap.get('phases', [])
    next_phase_number = len(current_phases) + 1

    # Get completed items for context
    completed_items = ProgressTracker.query.filter_by(
        user_id=user_id,
        status='completed'
    ).all()

    print(f"Extending roadmap for user {user_id}, phase {next_phase_number}")
    print(f"Found {len(completed_items)} completed items")

    # Generate next phase using Gemini
    roadmap_extension = gemini_service.generate_growth_path_extension(
        profile_data={
            'major': profile.major,
            'university': profile.university,
            'career_aspirations': profile.career_aspirations,
            'experience_level': profile.experience_level,
            'target_industries': profile.get_target_industries(),
            'current_skills': profile.get_skills(),
            'preferred_content_types': profile.get_preferred_content_types(),
            'time_commitment': profile.time_commitment,
            'planning_horizon_years': profile.planning_horizon_years or 1
        },
        analysis=profile.get_analysis(),
        completed_items=[{
            'name': item.item_name,
            'type': item.item_type,
            'completed_date': item.completion_date.isoformat() if item.completion_date else None
        } for item in completed_items],
        current_phase=next_phase_number,
        planning_horizon_years=profile.planning_horizon_years or 1
    )

    # Debug: Check what was generated
    print(f"Generated phase: {roadmap_extension.get('title', 'No title')}")
    print(f"Phase has {len(roadmap_extension.get('courses', []))} courses")
    print(f"Phase has {len(roadmap_extension.get('projects', []))} projects")
    print(f"Phase has {len(roadmap_extension.get('tests', []))} tests")
    print(f"Phase has {len(roadmap_extension.get('internships', []))} internships")
    print(f"Phase has {len(roadmap_extension.get('certificates', []))} certificates")

    # Add new phase to existing roadmap
    current_roadmap['phases'].append(roadmap_extension)
    current_path.set_roadmap(current_roadmap)
    current_path.phase = next_phase_number

    # Create progress trackers for new phase items
    new_phase = roadmap_extension
    tasks_created = 0
    
    for category in ['courses', 'tests', 'internships', 'certificates', 'projects']:
        items = new_phase.get(category, [])
        print(f"Processing {len(items)} items in category: {category}")
        
        for item in items:
            # Determine item type (remove 's' from plural category names)
            item_type = category[:-1] if category.endswith('s') else category
            
            # Get item name based on category - handle different field names
            if category == 'internships':
                item_name = item.get('type') or item.get('name') or 'Internship'
            elif category == 'tests':
                item_name = item.get('name') or 'Test'
            elif category == 'certificates':
                item_name = item.get('name') or 'Certificate'
            elif category == 'projects':
                item_name = item.get('name') or 'Project'
            else:  # courses
                item_name = item.get('name') or 'Course'
            
            # Ensure item has an ID
            if 'id' not in item:
                # Generate a unique ID if missing
                item_index = items.index(item) + 1
                item['id'] = f"{item_type[0]}{next_phase_number}{item_index}"
            
            print(f"Creating tracker for: {item_name} (id: {item['id']}, type: {item_type})")
            
            # Check if tracker already exists (prevent duplicates)
            existing_tracker = ProgressTracker.query.filter_by(
                user_id=user_id,
                item_id=item['id']
            ).first()
            
            if existing_tracker:
                print(f"Tracker already exists for {item['id']}, skipping")
            else:
                tracker = ProgressTracker(
                    user_id=user_id,
                    item_id=item['id'],
                    item_type=item_type,
                    item_name=item_name,
                    status='not_started'
                )
                db.session.add(tracker)
                tasks_created += 1
                print(f"Added tracker for {item_name}")

    db.session.commit()
    print(f"Created {tasks_created} new tasks for phase {next_phase_number}")
    
    if tasks_created == 0:
        print("WARNING: No tasks were created! Check if phase has items.")
        # Log the full phase structure for debugging
        print(f"Full phase structure: {json.dumps(roadmap_extension, indent=2)}")
    
    return roadmap_extension


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

    # Check if all tasks are completed and return flag for frontend
    all_completed = False
    if status == 'completed':
        try:
            all_tasks = ProgressTracker.query.filter_by(user_id=user_id).all()
            completed_tasks = [t for t in all_tasks if t.status == 'completed']
            all_completed = len(completed_tasks) == len(all_tasks) and len(all_tasks) > 0
        except Exception as e:
            print(f"Error checking for completion: {e}")

    return jsonify({
        'message': 'Progress updated successfully',
        'progress': tracker.to_dict(),
        'all_completed': all_completed
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
    user_profile = StudentProfile.query.filter_by(user_id=user_id).first()
    user = User.query.get(user_id)

    if not user_profile:
        return jsonify({'error': 'User profile not found'}), 404

    # Base resume structure
    full_resume = {
        'header': {
            'name': user.name,
            'email': user.email,
            'phone': user_profile.phone_number,
            'location': user_profile.relocation_goal or "Open to relocation",
            'linkedin': user_profile.linkedin_url,
            'github': user_profile.github_url,
            'portfolio': user_profile.portfolio_url,
        },
        'education': {
            'university': user_profile.university,
            'major': user_profile.major,
            'gpa': user_profile.gpa,
            'graduation_year': 'Present' # Placeholder or calculate
        },
        'skills': user_profile.get_skills(),
        'projects': [],
        'experience': [],
        'certifications': []
    }

    # Merge with auto-generated content if available
    if profile:
        generated_content = profile.get_resume()
        full_resume['projects'] = generated_content.get('projects', [])
        full_resume['experience'] = generated_content.get('experience', [])
        full_resume['certifications'] = generated_content.get('certifications', [])
        # If generated content has skills, maybe merge them or prefer them? 
        # For now, let's stick to the user's core skills plus any learned ones
        
    return jsonify({
        'resume': full_resume,
        'last_generated': profile.last_generated.isoformat() if profile else None
    }), 200




@app.route('/api/v1/profile/<int:user_id>/linkedin', methods=['GET'])
def get_linkedin_suggestions(user_id):
    """Get LinkedIn suggestions"""
    profile = ProfessionalProfile.query.filter_by(user_id=user_id).first()

    if not profile or not profile.get_linkedin():
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