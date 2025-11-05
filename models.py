from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models."""

    pass


class User(Base):
    """User Model - Core authentication and identity"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationships
    personal_info: Mapped[Optional["PersonalInfo"]] = relationship(
        "PersonalInfo",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    summary: Mapped[Optional["Summary"]] = relationship(
        "Summary", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    education: Mapped[List["Education"]] = relationship(
        "Education", back_populates="user", cascade="all, delete-orphan"
    )
    experiences: Mapped[List["Experience"]] = relationship(
        "Experience", back_populates="user", cascade="all, delete-orphan"
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="user", cascade="all, delete-orphan"
    )
    technical_skills: Mapped[List["TechnicalSkill"]] = relationship(
        "TechnicalSkill", back_populates="user", cascade="all, delete-orphan"
    )
    publications: Mapped[List["Publication"]] = relationship(
        "Publication", back_populates="user", cascade="all, delete-orphan"
    )
    certifications: Mapped[List["Certification"]] = relationship(
        "Certification", back_populates="user", cascade="all, delete-orphan"
    )
    custom_sections: Mapped[List["CustomSection"]] = relationship(
        "CustomSection", back_populates="user", cascade="all, delete-orphan"
    )
    resumes: Mapped[List["Resume"]] = relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User: {self.username}>"


class PersonalInfo(Base):
    """PersonalInfo Model - Stores user contact and personal details"""

    __tablename__ = "personal_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    github_url: Mapped[Optional[str]] = mapped_column(String(500))
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(500))
    website_url: Mapped[Optional[str]] = mapped_column(String(500))
    professional_title: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="personal_info")

    def __repr__(self):
        return f"<PersonalInfo: {self.full_name}>"


class Summary(Base):
    """Summary Model - Stores professional summary with AI enhancement"""

    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False
    )

    # User's original input
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)

    # AI-enhanced version
    summary_enhanced: Mapped[Optional[str]] = mapped_column(Text)

    # Enhancement tracking
    is_ai_generated: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    enhancement_prompt_used: Mapped[Optional[str]] = mapped_column(Text)
    last_enhanced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="summary")

    def __repr__(self):
        return f"<Summary: User {self.user_id}>"


class Education(Base):
    """Education Model - Stores academic background"""

    __tablename__ = "education"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    institution_name: Mapped[str] = mapped_column(String(255), nullable=False)
    degree: Mapped[str] = mapped_column(String(255), nullable=False)
    field_of_study: Mapped[Optional[str]] = mapped_column(String(255))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    grade: Mapped[Optional[str]] = mapped_column(String(50))
    location: Mapped[Optional[str]] = mapped_column(String(255))

    # User's original description
    description: Mapped[Optional[str]] = mapped_column(Text)

    # AI-enhanced version
    description_enhanced: Mapped[Optional[str]] = mapped_column(Text)

    # Enhancement tracking
    enhancement_prompt_used: Mapped[Optional[str]] = mapped_column(Text)
    last_enhanced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="education")

    def __repr__(self):
        return f"<Education: {self.degree} at {self.institution_name}>"


class Experience(Base):
    """Experience Model - Stores work history with AI enhancement"""

    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    employment_type: Mapped[Optional[str]] = mapped_column(String(50))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # User's original input
    description: Mapped[Optional[str]] = mapped_column(Text)
    achievements: Mapped[Optional[dict]] = mapped_column(JSON)  # Array of strings

    # AI-enhanced versions
    description_enhanced: Mapped[Optional[str]] = mapped_column(Text)
    achievements_enhanced: Mapped[Optional[dict]] = mapped_column(
        JSON
    )  # Array of strings

    # Enhancement tracking
    enhancement_prompt_used: Mapped[Optional[str]] = mapped_column(Text)
    last_enhanced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    technologies_used: Mapped[Optional[dict]] = mapped_column(JSON)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="experiences")

    def __repr__(self):
        return f"<Experience: {self.job_title} at {self.company_name}>"


class Project(Base):
    """Project Model - Stores portfolio projects with AI enhancement"""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # User's original input
    description: Mapped[str] = mapped_column(Text, nullable=False)
    highlights: Mapped[Optional[dict]] = mapped_column(JSON)  # Array of strings

    # AI-enhanced versions
    description_enhanced: Mapped[Optional[str]] = mapped_column(Text)
    highlights_enhanced: Mapped[Optional[dict]] = mapped_column(
        JSON
    )  # Array of strings

    # Enhancement tracking
    enhancement_prompt_used: Mapped[Optional[str]] = mapped_column(Text)
    last_enhanced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    project_url: Mapped[Optional[str]] = mapped_column(String(500))
    github_url: Mapped[Optional[str]] = mapped_column(String(500))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    technologies_used: Mapped[Optional[dict]] = mapped_column(JSON)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="projects")

    def __repr__(self):
        return f"<Project: {self.project_name}>"


class TechnicalSkill(Base):
    """TechnicalSkill Model - Stores grouped technical skills"""

    __tablename__ = "technical_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    skills: Mapped[dict] = mapped_column(JSON, nullable=False)  # Array of skill names
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="technical_skills")

    def __repr__(self):
        return f"<TechnicalSkill: {self.category}>"


class Publication(Base):
    """Publication Model - Stores research papers and publications"""

    __tablename__ = "publications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    authors: Mapped[Optional[str]] = mapped_column(Text)
    publication_venue: Mapped[Optional[str]] = mapped_column(String(255))
    publication_date: Mapped[Optional[date]] = mapped_column(Date)
    doi: Mapped[Optional[str]] = mapped_column(String(255))
    url: Mapped[Optional[str]] = mapped_column(String(500))

    # User's original description
    description: Mapped[Optional[str]] = mapped_column(Text)

    # AI-enhanced version
    description_enhanced: Mapped[Optional[str]] = mapped_column(Text)

    # Enhancement tracking
    enhancement_prompt_used: Mapped[Optional[str]] = mapped_column(Text)
    last_enhanced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="publications")

    def __repr__(self):
        return f"<Publication: {self.title}>"


class Certification(Base):
    """Certification Model - Stores professional certifications"""

    __tablename__ = "certifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    certification_name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuing_organization: Mapped[str] = mapped_column(String(255), nullable=False)
    issue_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    credential_id: Mapped[Optional[str]] = mapped_column(String(255))
    credential_url: Mapped[Optional[str]] = mapped_column(String(500))

    # User's original description
    description: Mapped[Optional[str]] = mapped_column(Text)

    # AI-enhanced version
    description_enhanced: Mapped[Optional[str]] = mapped_column(Text)

    # Enhancement tracking
    enhancement_prompt_used: Mapped[Optional[str]] = mapped_column(Text)
    last_enhanced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="certifications")

    def __repr__(self):
        return f"<Certification: {self.certification_name}>"


class CustomSection(Base):
    """CustomSection Model - Stores flexible user-defined sections with AI enhancement"""

    __tablename__ = "custom_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    section_title: Mapped[str] = mapped_column(String(255), nullable=False)

    # User's original content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # AI-enhanced version
    content_enhanced: Mapped[Optional[str]] = mapped_column(Text)

    # Enhancement tracking
    enhancement_prompt_used: Mapped[Optional[str]] = mapped_column(Text)
    last_enhanced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="custom_sections")

    def __repr__(self):
        return f"<CustomSection: {self.section_title}>"


class Resume(Base):
    """Resume Model - Stores generated resume records"""

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    company_name: Mapped[Optional[str]] = mapped_column(String(255))
    position_title: Mapped[Optional[str]] = mapped_column(String(255))
    generated_content: Mapped[Optional[str]] = mapped_column(Text)
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(
        String(50), default="processing", nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Track which prompt was used for generation
    generation_prompt_used: Mapped[Optional[str]] = mapped_column(Text)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="resumes")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self):
        return f"<Resume: {self.id} for User {self.user_id}>"
