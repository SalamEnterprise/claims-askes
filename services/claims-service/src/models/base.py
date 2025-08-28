"""
Base Model for SQLAlchemy
Shared base class for all models
"""

from sqlalchemy.ext.declarative import declarative_base

# Create base class for declarative models
Base = declarative_base()