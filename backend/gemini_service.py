import google.generativeai as genai
import json
import os
from typing import Dict, List, Optional


class GeminiService:
    """
    Orchestrates all interactions with Gemini 2.5 API
    """

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

        # Generation configuration
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_output_tokens": 8192,
        }

    def analyze_student_profile(self, profile_data: Dict) -> Dict:
        """
        Analyze student profile and provide insights
        """
        prompt = f"""
You are an expert career advisor analyzing a student's profile.

Student Information:
- Major: {profile_data.get('major', 'Not specified')}
- University: {profile_data.get('university', 'Not specified')}
- GPa: {profile_data.get('gpa', 'Not specified')}
- Experience Level: {profile_data.get('experience_level', 'Not specified')}
- Career Aspirations: {profile_data.get('career_aspirations', 'Not specified')}
- Target Industries: {', '.join(profile_data.get('target_industries', []))}
- Current Skills: {', '.join(profile_data.get('current_skills', []))}
- Preferred Learning Style: {profile_data.get('preferred_learning', 'Not specified')}
- Preferred Content Types: {', '.join(profile_data.get('preferred_content_types', []))}
- Time Commitment: {profile_data.get('time_commitment', 'Not specified')}
- Relocation Goal: {profile_data.get('relocation_goal', 'None')}
- Extracurricular Interests: {', '.join(profile_data.get('extracurricular_interests', []))}
- Planning Horizon: {profile_data.get('planning_horizon_years', 1)} Years

Task: Analyze this profile and provide:
1. Key strengths (2-3 points)
2. Skill gaps to address (2-3 points)
3. Recommended career paths (top 3, ordered from most specific to broad)
4. Learning approach optimization tips (2-3 actionable tips)
5. Advice on relocation and extracurricular balance (if applicable)

Format your response as JSON with keys: "strengths", "gaps", "career_paths", "learning_tips"
Each value should be an array of strings.

Return ONLY valid JSON, no additional text.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            # Extract JSON from response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())
            return result

        except Exception as e:
            print(f"Error in analyze_student_profile: {e}")
            return {
                "strengths": ["Motivated to learn", "Clear career direction"],
                "gaps": ["Need more hands-on experience"],
                "career_paths": ["Technology Professional", "Industry Specialist", "General Professional"],
                "learning_tips": ["Start with foundational courses", "Build portfolio projects"]
            }

    def generate_growth_path(self, profile_data: Dict, analysis: Dict, timeline_months: int = 12) -> Dict:
        """
        Generate comprehensive phased growth path
        """

        # Simulate trend data
        trend_data = self._get_simulated_trends(profile_data.get('career_aspirations', ''))

        target_role = analysis.get('career_paths', ['Professional'])[0]
        skill_gaps = ', '.join(analysis.get('gaps', []))

        years = int(profile_data.get('planning_horizon_years', 1))
        
        prompt = f"""
You are an expert educational and career strategist creating a personalized {years}-year growth roadmap.

Student Profile:
- Major: {profile_data.get('major')}
- University: {profile_data.get('university')}
- Target Role: {target_role}
- Target Industries: {', '.join(profile_data.get('target_industries', []))}
- Experience Level: {profile_data.get('experience_level')}
- Current Skills: {', '.join(profile_data.get('current_skills', []))}
- Skill Gaps: {skill_gaps}
- Time Commitment: {profile_data.get('time_commitment')}
- Content Preference: {', '.join(profile_data.get('preferred_content_types', []))}
- Relocation Goal: {profile_data.get('relocation_goal', 'None')}
- Extracurricular Interests: {', '.join(profile_data.get('extracurricular_interests', []))}
- Planning Horizon: {years} Years

Current Industry Trends:
{trend_data}

Task: Generate a detailed, phased growth plan with {years} phases, where each phase represents 1 YEAR.

For each phase (Year), provide:

1. **Courses**: 2-3 specific online courses with name, platform, estimated duration, and clear rationale
2. **Tests/Certifications**: Relevant exams with target scores, timing, and rationale
3. **Internships/Jobs**: Types, timing, target companies/industries, and rationale
4. **Extracurricular Activities**: Clubs, hobbies, or volunteering aligned with interests and goals
5. **Projects**: 2-3 practical projects with name, description, skills demonstrated, and rationale
6. **Weekly Routine**: A friendly, sample weekly schedule (e.g., "Mon/Wed: German Class, Sat: Coding Project") tailored to this phase's goals.

Guidelines:
- **Long-term View**: If relocation is a goal (e.g., to Germany), include language learning (A1-C1) and visa prep in earlier years.
- **Holistic**: Integrate extracurriculars to build soft skills.
- **Friendly Tone**: The "Weekly Routine" should sound encouraging and doable.
- **Progression**: ensuring skills build up year over year.

Format as JSON with this EXACT structure:
{{
  "phases": [
    {{
      "phase": 1,
      "title": "Year 1: [Theme Name]",
      "focus": "Main focus of this year",
      "weekly_routine": "Sample weekly schedule (e.g., Mon-Fri: ... Sat: ...)",
      "courses": [
        {{
          "id": "c1",
          "name": "Course Name",
          "platform": "Platform Name",
          "duration": "X weeks",
          "rationale": "Why this course"
        }}
      ],
      "tests": [
        {{
          "id": "t1",
          "name": "Test Name",
          "target_score": "Score or Grade",
          "timing": "When to take",
          "rationale": "Why this test"
        }}
      ],
      "internships": [
        {{
          "id": "i1",
          "type": "Internship Type",
          "when": "Application timeline",
          "companies": ["Company examples"],
          "rationale": "Why this internship"
        }}
      ],
      "certificates": [
        {{
          "id": "cert1",
          "name": "Certificate Name",
          "provider": "Provider Name",
          "timing": "When to get",
          "rationale": "Why this certificate"
        }}
      ],
      "projects": [
        {{
          "id": "p1",
          "name": "Project Name",
          "description": "Project description",
          "skills_demonstrated": ["skill1", "skill2"],
          "rationale": "Why this project"
        }}
      ]
    }}
  ]
}}

Return ONLY valid JSON, no additional text or markdown.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            response_text = response.text.strip()

            # Clean response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())
            return result

        except Exception as e:
            print(f"Error in generate_growth_path: {e}")
            return self._get_fallback_roadmap(target_role)

    def generate_encouragement(self, completed_item: Dict, user_context: Dict) -> str:
        """
        Generate personalized encouragement message
        """
        prompt = f"""
A student just completed: {completed_item.get('item_name')} ({completed_item.get('item_type')})

Student's journey so far:
- Completed items: {user_context.get('completed_count', 0)}
- Current phase: {user_context.get('current_phase', 1)}
- Career goal: {user_context.get('career_goal', 'Professional development')}

Generate a brief, encouraging message (2-3 sentences) that:
1. Acknowledges their specific achievement
2. Connects it to their career goal
3. Motivates next steps

Keep it genuine, specific, and energizing. Do not use emojis.
Return only the message text, nothing else.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.8, "max_output_tokens": 200}
            )
            return response.text.strip()

        except Exception as e:
            print(f"Error in generate_encouragement: {e}")
            return f"Great work completing {completed_item.get('item_name')}! You're making excellent progress toward your goals. Keep up the momentum!"

    def generate_resume_bullets(self, item_data: Dict) -> List[str]:
        """
        Generate professional resume bullet points
        """
        prompt = f"""
Generate professional resume bullet points for:

Type: {item_data.get('item_type')}
Title: {item_data.get('title')}
Description: {item_data.get('description', 'Not provided')}
Skills Used: {', '.join(item_data.get('skills', []))}
Target Role: {item_data.get('target_role', 'Professional')}

Guidelines:
- Start with strong action verbs (Developed, Implemented, Designed, Led, etc.)
- Include quantifiable metrics where possible
- Highlight technical skills and tools
- Show impact and results
- 2-3 bullet points
- Each bullet: 1-2 lines maximum

Format as JSON array:
{{"bullets": ["bullet 1", "bullet 2", "bullet 3"]}}

Return ONLY valid JSON, no additional text.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.7, "max_output_tokens": 500}
            )

            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())
            return result.get('bullets', [])

        except Exception as e:
            print(f"Error in generate_resume_bullets: {e}")
            return [
                f"Completed {item_data.get('title')} demonstrating proficiency in {', '.join(item_data.get('skills', ['various skills']))}",
                f"Applied technical knowledge to solve real-world problems in {item_data.get('item_type')} context"
            ]

    def generate_linkedin_content(self, user_context: Dict) -> Dict:
        """
        Generate LinkedIn post ideas and profile updates
        """
        prompt = f"""
Generate LinkedIn content suggestions for a student with:

Profile:
- Recent achievements: {', '.join(user_context.get('recent_achievements', []))}
- New skills: {', '.join(user_context.get('new_skills', []))}
- Career goal: {user_context.get('career_goal', 'Professional development')}
- Current phase: {user_context.get('current_phase', 'Learning')}

Generate:
1. **Post Ideas**: 3 LinkedIn post ideas that showcase their learning journey and achievements
2. **Profile Summary**: A 2-3 sentence professional summary highlighting their skills and aspirations
3. **Skills to Add**: 5-7 skills they should add to their LinkedIn profile

Format as JSON:
{{
  "post_ideas": [
    {{"topic": "...", "draft": "...", "hashtags": ["..."]}},
    ...
  ],
  "profile_summary": "...",
  "skills_to_add": ["skill1", "skill2", ...]
}}

Return ONLY valid JSON, no additional text.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.8, "max_output_tokens": 1000}
            )

            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())
            return result

        except Exception as e:
            print(f"Error in generate_linkedin_content: {e}")
            return {
                "post_ideas": [
                    {
                        "topic": "Learning Journey",
                        "draft": f"Excited to share my progress in {user_context.get('career_goal', 'my career development')}!",
                        "hashtags": ["learning", "growth", "career"]
                    }
                ],
                "profile_summary": f"Aspiring professional focused on {user_context.get('career_goal', 'continuous learning')} with hands-on experience in recent projects.",
                "skills_to_add": user_context.get('new_skills', ["Problem Solving", "Project Management"])
            }

    def _get_simulated_trends(self, career_field: str) -> str:
        """
        Generate simulated industry trends
        """
        common_trends = """
Current Industry Trends (2025-2026):
- AI and Machine Learning integration across all sectors
- Cloud computing and distributed systems dominance
- Data privacy and cybersecurity critical importance
- Remote work and digital collaboration tools
- Sustainability and green technology focus
- API-first and microservices architectures
- Low-code/no-code platforms emergence
"""
        return common_trends

    def _get_fallback_roadmap(self, target_role: str) -> Dict:
        """
        Fallback roadmap if Gemini fails
        """
        return {
            "phases": [
                {
                    "phase": 1,
                    "title": "Foundation Building (Months 1-3)",
                    "focus": "Build core fundamentals",
                    "courses": [
                        {
                            "id": "c1",
                            "name": "Introduction to Programming",
                            "platform": "Coursera",
                            "duration": "4 weeks",
                            "rationale": "Essential programming foundation"
                        }
                    ],
                    "tests": [],
                    "internships": [],
                    "certificates": [],
                    "projects": [
                        {
                            "id": "p1",
                            "name": "Personal Portfolio Website",
                            "description": "Build a professional portfolio",
                            "skills_demonstrated": ["HTML", "CSS", "JavaScript"],
                            "rationale": "Demonstrate web development skills"
                        }
                    ]
                }
            ]
        }