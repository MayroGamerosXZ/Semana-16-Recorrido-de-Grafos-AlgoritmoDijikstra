from dataclasses import dataclass
from datetime import datetime


@dataclass
class Package:
    id: str
    address: str
    latitude: float
    longitude: float
    priority: int  # 1 (high) to 3 (low)
    delivery_time: datetime = None
    status: str = "pending"  # pending, in_transit, delivered

    def to_dict(self):
        """Convert package to dictionary format."""
        return {
            "id": self.id,
            "address": self.address,
            "coordinates": (self.latitude, self.longitude),
            "priority": self.priority,
            "delivery_time": self.delivery_time,
            "status": self.status
        }
