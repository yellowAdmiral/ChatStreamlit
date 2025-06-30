
from pydantic import BaseModel
from typing import List, Optional

class Skill(BaseModel):
    skill_subcategory: str
    skill_list: List[str]

class Experience(BaseModel):
    role: str
    company_name: str
    location: Optional[str]
    date_from: str
    date_to: str
    responsibilities: List[str]

class Education(BaseModel):
    degree: str
    university: str
    grade: Optional[str] = None
    date_from: str
    date_to: str

class Project(BaseModel):
    project_title: str
    description: List[str]

class ContactDetails(BaseModel):
    phone_number: Optional[str]
    email_id: str

class CV(BaseModel):
    full_name: str
    contact_details: ContactDetails
    linkedin: str
    github: Optional[str] = None
    personal_profile: str
    skills: List[Skill]
    experience: List[Experience]
    education: List[Education]
    projects: List[Project]
