from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    onboarding_complete = db.Column(db.Boolean, default=False)

    # Relationships
    profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    growth_paths = db.relationship('GrowthPath', backref='user', cascade='all, delete-orphan')
    progress = db.relationship('ProgressTracker', backref='user', cascade='all, delete-orphan')
    professional_profile = db.relationship('ProfessionalProfile', backref='user', uselist=False,
                                           cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'onboarding_complete': self.onboarding_complete
        }


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    major = db.Column(db.String(255))
    university = db.Column(db.String(255))
    gpa = db.Column(db.Float)
    career_aspirations = db.Column(db.Text)
    current_skills = db.Column(db.Text)  # JSON string
    experience_level = db.Column(db.String(50))
    target_industries = db.Column(db.Text)  # JSON string
    preferred_learning = db.Column(db.String(100))
    preferred_content_types = db.Column(db.Text)  # JSON string
    time_commitment = db.Column(db.String(50))
    analysis_data = db.Column(db.Text)  # JSON string - Gemini analysis results
    
    # New Fields for Long-term Planning
    profile_photo = db.Column(db.Text)  # Base64 string or URL
    relocation_goal = db.Column(db.String(255))
    extracurricular_interests = db.Column(db.Text)  # JSON string
    planning_horizon_years = db.Column(db.Integer, default=1)
    
    # Contact & Social Links
    phone_number = db.Column(db.String(50))
    linkedin_url = db.Column(db.String(255))
    github_url = db.Column(db.String(255))
    portfolio_url = db.Column(db.String(255))

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_skills(self):
        return json.loads(self.current_skills) if self.current_skills else []

    def set_skills(self, skills_list):
        self.current_skills = json.dumps(skills_list)

    def get_target_industries(self):
        return json.loads(self.target_industries) if self.target_industries else []

    def set_target_industries(self, industries_list):
        self.target_industries = json.dumps(industries_list)

    def get_preferred_content_types(self):
        return json.loads(self.preferred_content_types) if self.preferred_content_types else []

    def set_preferred_content_types(self, content_types_list):
        self.preferred_content_types = json.dumps(content_types_list)

    def get_extracurricular_interests(self):
        return json.loads(self.extracurricular_interests) if self.extracurricular_interests else []

    def set_extracurricular_interests(self, interests_list):
        self.extracurricular_interests = json.dumps(interests_list)

    def get_analysis(self):
        return json.loads(self.analysis_data) if self.analysis_data else {}

    def set_analysis(self, analysis_dict):
        self.analysis_data = json.dumps(analysis_dict)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'major': self.major,
            'university': self.university,
            'gpa': self.gpa,
            'career_aspirations': self.career_aspirations,
            'current_skills': self.get_skills(),
            'experience_level': self.experience_level,
            'target_industries': self.get_target_industries(),
            'preferred_learning': self.preferred_learning,
            'preferred_content_types': self.get_preferred_content_types(),
            'time_commitment': self.time_commitment,
            'profile_photo': self.profile_photo,
            'relocation_goal': self.relocation_goal,
            'extracurricular_interests': self.get_extracurricular_interests(),
            'planning_horizon_years': self.planning_horizon_years,
            'phone_number': self.phone_number,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'portfolio_url': self.portfolio_url,
            'analysis': self.get_analysis(),
            'updated_at': self.updated_at.isoformat()
        }


class GrowthPath(db.Model):
    __tablename__ = 'growth_paths'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    phase = db.Column(db.Integer, nullable=False)
    roadmap_data = db.Column(db.Text, nullable=False)  # JSON string
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def get_roadmap(self):
        return json.loads(self.roadmap_data) if self.roadmap_data else {}

    def set_roadmap(self, roadmap_dict):
        self.roadmap_data = json.dumps(roadmap_dict)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'phase': self.phase,
            'roadmap': self.get_roadmap(),
            'generated_at': self.generated_at.isoformat(),
            'is_active': self.is_active
        }


class ProgressTracker(db.Model):
    __tablename__ = 'progress_tracker'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.String(50), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)  # course, test, internship, certificate, project
    item_name = db.Column(db.String(255))
    status = db.Column(db.String(50), default='not_started')  # not_started, in_progress, completed
    completion_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    encouragement_message = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'item_id': self.item_id,
            'item_type': self.item_type,
            'item_name': self.item_name,
            'status': self.status,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'notes': self.notes,
            'encouragement_message': self.encouragement_message
        }


class ProfessionalProfile(db.Model):
    __tablename__ = 'professional_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resume_json = db.Column(db.Text)  # JSON string
    linkedin_suggestions = db.Column(db.Text)  # JSON string
    last_generated = db.Column(db.DateTime, default=datetime.utcnow)

    def get_resume(self):
        return json.loads(self.resume_json) if self.resume_json else {}

    def set_resume(self, resume_dict):
        self.resume_json = json.dumps(resume_dict)

    def get_linkedin(self):
        return json.loads(self.linkedin_suggestions) if self.linkedin_suggestions else {}

    def set_linkedin(self, linkedin_dict):
        self.linkedin_suggestions = json.dumps(linkedin_dict)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resume': self.get_resume(),
            'linkedin_suggestions': self.get_linkedin(),
            'last_generated': self.last_generated.isoformat()
        }


class SimulatedTrend(db.Model):
    __tablename__ = 'simulated_trends'

    id = db.Column(db.Integer, primary_key=True)
    industry = db.Column(db.String(255), nullable=False)
    trend_data = db.Column(db.Text, nullable=False)  # JSON string
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_trends(self):
        return json.loads(self.trend_data) if self.trend_data else {}

    def set_trends(self, trends_dict):
        self.trend_data = json.dumps(trends_dict)

    def to_dict(self):
        return {
            'id': self.id,
            'industry': self.industry,
            'trends': self.get_trends(),
            'generated_at': self.generated_at.isoformat()
        }