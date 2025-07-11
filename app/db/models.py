from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum, Text, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base_class import Base

import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

# Association tables
project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)

class EntityType(str, enum.Enum):
    SPEC = "spec"
    PROJECT = "project"
    LINT_RESULT = "lint_result"

class NotificationType(str, enum.Enum):
    COMMENT = "comment"
    UPDATE = "update"
    MENTION = "mention"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String)  # admin, engineer, pm
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    companies = relationship("Company", back_populates="owner")
    projects = relationship("Project", secondary=project_members, back_populates="members")
    comments = relationship("Comment", back_populates="author")
    notifications = relationship("Notification", back_populates="recipient")
    notification_preferences = relationship("NotificationPreference", back_populates="user")

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String, default="Active")

    # Relationships
    owner = relationship("User", back_populates="companies")
    projects = relationship("Project", back_populates="company")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="projects")
    members = relationship("User", secondary=project_members, back_populates="projects")
    specs = relationship("Spec", back_populates="project")
    comments = relationship("Comment", back_populates="project")

class Spec(Base):
    __tablename__ = "specs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    version = Column(String)
    status = Column(Enum("draft", "review", "approved", "archived", name="spec_status"))
    file_path = Column(String)
    project_id = Column(Integer, ForeignKey("projects.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    spec_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="specs")
    lint_results = relationship("LintResult", back_populates="spec")
    comments = relationship("Comment", back_populates="spec")

class LintResult(Base):
    __tablename__ = "lint_results"

    id = Column(Integer, primary_key=True, index=True)
    spec_id = Column(Integer, ForeignKey("specs.id"))
    issues = Column(JSON)
    summary = Column(String)
    spec_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    spec = relationship("Spec", back_populates="lint_results")
    comments = relationship("Comment", back_populates="lint_result")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    entity_type = Column(Enum(EntityType))
    entity_id = Column(Integer)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    spec_id = Column(Integer, ForeignKey("specs.id"), nullable=True)
    lint_result_id = Column(Integer, ForeignKey("lint_results.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author = relationship("User", back_populates="comments")
    project = relationship("Project", back_populates="comments")
    spec = relationship("Spec", back_populates="comments")
    lint_result = relationship("LintResult", back_populates="comments")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"))
    type = Column(Enum(NotificationType))
    entity_type = Column(Enum(EntityType))
    entity_id = Column(Integer)
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    recipient = relationship("User", back_populates="notifications")

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    notification_type = Column(Enum(NotificationType))
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="notification_preferences")

class Specification(Base):
    __tablename__ = "specifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    uploaded_by = Column(String, nullable=False)
    uploaded_on = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Pending")
    assigned_to = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    approved_by = Column(String, nullable=True)
    rejected_by = Column(String, nullable=True)

class Checklist(Base):
    __tablename__ = "checklists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ChecklistTemplate(Base):
    __tablename__ = "checklist_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    items = relationship("ChecklistItem", back_populates="template", cascade="all, delete-orphan")

class ChecklistItem(Base):
    __tablename__ = "checklist_items"
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("checklist_templates.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    template = relationship("ChecklistTemplate", back_populates="items")

class ActiveChecklist(Base):
    __tablename__ = "active_checklists"
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("checklist_templates.id"), nullable=False)
    linked_spec_id = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    items = relationship("ActiveChecklistItem", back_populates="checklist", cascade="all, delete-orphan")

class ActiveChecklistItem(Base):
    __tablename__ = "active_checklist_items"
    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey("active_checklists.id"), nullable=False)
    template_item_id = Column(Integer, ForeignKey("checklist_items.id"), nullable=False)
    status = Column(String, default="pending")  # pending, done, in_progress
    comment = Column(String, nullable=True)
    evidence_file_path = Column(String, nullable=True)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    checklist = relationship("ActiveChecklist", back_populates="items")
    template_item = relationship("ChecklistItem")
    assigned_user = relationship("User") 