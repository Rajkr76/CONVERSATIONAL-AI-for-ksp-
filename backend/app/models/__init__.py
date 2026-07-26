"""Models package — exports all SQLAlchemy models."""

from app.models.user import User
from app.models.officer import Officer
from app.models.fir import FIR
from app.models.accused import Accused
from app.models.victim import Victim
from app.models.investigation import Investigation
from app.models.evidence import Evidence
from app.models.witness import Witness
from app.models.criminal_history import CriminalHistory
from app.models.financial_transaction import FinancialTransaction
from app.models.location_history import LocationHistory
from app.models.chat_history import ChatHistory

__all__ = [
    "User", "Officer", "FIR", "Accused", "Victim",
    "Investigation", "Evidence", "Witness", "CriminalHistory",
    "FinancialTransaction", "LocationHistory", "ChatHistory",
]
