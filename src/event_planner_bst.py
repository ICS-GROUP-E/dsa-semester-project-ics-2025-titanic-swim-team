import datetime
import logging
from typing import Optional, List
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Event class
@dataclass
class Event:
    event_id: int
    name: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    location: str
    description: str
    attendees: str  # Comma-separated names
    reminder_set: bool

# Node for Binary Search Tree
class BSTNode:
    def __init__(self, event: Event):
        self.event = event
        self.left = None
        self.right = None

# Event Planner class with BST functionality
class EventPlanner:
    def __init__(self):
        self.bst_root = None  # Root of BST for events
        self.event_id_counter = 1
        logger.info("EventPlanner initialized")
        print("EventPlanner initialized")

    @staticmethod
    def _get_datetime(date: str, time: str) -> datetime.datetime:
        """Parse and validate date/time."""
        try:
            dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            logger.debug(f"Parsed datetime: {dt}")
            return dt
        except ValueError:
            logger.error(f"Invalid date/time format: {date} {time}")
            raise ValueError("Use YYYY-MM-DD HH:MM")

    def create_event(self, name: str, date: str, time: str, location: str, description: str, attendees: str, reminder_set: bool) -> Event:
        """Create a new event and insert into BST."""
        logger.info(f"Creating event: {name}, {date} {time}")
        self._get_datetime(date, time)
        event = Event(self.event_id_counter, name, date, time, location, description, attendees, reminder_set)
        self._insert_bst(event)
        self.event_id_counter += 1
        logger.info(f"Event created: ID={event.event_id}")
        print(f"Created event: {event.name} (ID: {event.event_id}) on {event.date} at {event.time}")
        return event

    def _insert_bst(self, event: Event) -> None:
        """Insert event into BST based on date and time."""
        logger.debug(f"Inserting event {event.name} into BST")
        if not self.bst_root:
            self.bst_root = BSTNode(event)
        else:
            self._insert_bst_recursive(self.bst_root, event)

    def _insert_bst_recursive(self, node: BSTNode, event: Event) -> None:
        event_dt = self._get_datetime(event.date, event.time)
        node_dt = self._get_datetime(node.event.date, node.event.time)
        if event_dt < node_dt:
            if node.left is None:
                node.left = BSTNode(event)
                logger.debug(f"Inserted {event.name} as left child")
            else:
                self._insert_bst_recursive(node.left, event)
        else:
            if node.right is None:
                node.right = BSTNode(event)
                logger.debug(f"Inserted {event.name} as right child")
            else:
                self._insert_bst_recursive(node.right, event)

    def update_event(self, event_id: int, name: Optional[str] = None, date: Optional[str] = None, 
                    time: Optional[str] = None, location: Optional[str] = None, 
                    description: Optional[str] = None, attendees: Optional[str] = None, 
                    reminder_set: Optional[bool] = None) -> Optional[Event]:
        """Update event details and reinsert into BST if date/time changes."""
        logger.info(f"Updating event ID={event_id}")
        event = self._find_event(self.bst_root, event_id)
        if not event:
            logger.warning(f"Event {event_id} not found")
            print(f"Error: Event ID {event_id} not found")
            return None
        old_event = event
        if date or time:
            self._get_datetime(date or old_event.date, time or old_event.time)
        if name is not None:
            old_event.name = name
        if date is not None:
            old_event.date = date
        if time is not None:
            old_event.time = time
        if location is not None:
            old_event.location = location
        if description is not None:
            old_event.description = description
        if attendees is not None:
            old_event.attendees = attendees
        if reminder_set is not None:
            old_event.reminder_set = reminder_set
        if date or time:
            self._delete_bst_node(self.bst_root, event_id)
            self._insert_bst(old_event)
        logger.info(f"Event {event_id} updated")
        print(f"Updated event: {old_event.name} (ID: {event_id})")
        return old_event

    def _find_event(self, node: Optional[BSTNode], event_id: int) -> Optional[Event]:
        """Find event by ID in BST."""
        if not node:
            return None
        if node.event.event_id == event_id:
            logger.debug(f"Found event ID={event_id}")
            return node.event
        left = self._find_event(node.left, event_id)
        if left:
            return left
        return self._find_event(node.right, event_id)

    def _delete_bst_node(self, node: Optional[BSTNode], event_id: int) -> Optional[BSTNode]:
        """Delete event from BST."""
        if not node:
            return None
        if node.event.event_id == event_id:
            logger.debug(f"Deleting event ID={event_id}")
            if not node.left:
                return node.right
            elif not node.right:
                return node.left
            successor = self._find_min(node.right)
            node.event = successor.event
            node.right = self._delete_bst_node(node.right, successor.event.event_id)
            return node
        if self._get_datetime(node.event.date, node.event.time) > self._get_datetime(self._find_event(node.left, event_id).date, self._find_event(node.left, event_id).time) if node.left else datetime.datetime.max:
            node.left = self._delete_bst_node(node.left, event_id)
        else:
            node.right = self._delete_bst_node(node.right, event_id)
        return node

    def _find_min(self, node: BSTNode) -> BSTNode:
        """Find minimum node in BST."""
        current = node
        while current.left:
            current = current.left
        logger.debug(f"Found minimum node: {current.event.name}")
        return current

    def delete_event(self, event_id: int) -> bool:
        """Delete an event from BST."""
        logger.info(f"Deleting event ID={event_id}")
        event = self._find_event(self.bst_root, event_id)
        if not event:
            logger.warning(f"Event {event_id} not found")
            print(f"Error: Event ID {event_id} not found")
            return False
        self.bst_root = self._delete_bst_node(self.bst_root, event_id)
        logger.info(f"Event {event_id} deleted")
        print(f"Deleted event: {event.name} (ID: {event_id})")
        return True

    def view_events(self, upcoming: bool = True) -> List[Event]:
        """View events in chronological order with upcoming/past filter."""
        current_date = datetime.datetime.now()
        events = []
        self._inorder_traversal(self.bst_root, events, current_date, upcoming)
        logger.info(f"Viewing {'upcoming' if upcoming else 'past'} events: {len(events)}")
        print(f"\n{'Upcoming' if upcoming else 'Past'} Events:")
        for event in events:
            print(f"ID: {event.event_id}, Name: {event.name}, Date: {event.date}, Time: {event.time}, Location: {event.location}")
        return events

    def _inorder_traversal(self, node: Optional[BSTNode], events: List[Event], current_date: datetime.datetime, upcoming: bool) -> None:
        """In-order traversal of BST with date filter."""
        if node:
            self._inorder_traversal(node.left, events, current_date, upcoming)
            event_dt = self._get_datetime(node.event.date, node.event.time)
            if (upcoming and event_dt >= current_date) or (not upcoming and event_dt < current_date):
                events.append(node.event)
            self._inorder_traversal(node.right, events, current_date, upcoming)

def main():
    """Demonstrate EventPlanner functionality."""
    planner = EventPlanner()
    
    # Create sample events
    try:
        event1 = planner.create_event(
            name="Team Meeting",
            date="2025-07-10",
            time="15:00",
            location="Office",
            description="Discuss project",
            attendees="Alice,Bob",
            reminder_set=True
        )
        event2 = planner.create_event(
            name="Client Call",
            date="2025-07-15",
            time="10:00",
            location="Online",
            description="Review progress",
            attendees="Charlie",
            reminder_set=False
        )
    except ValueError as e:
        logger.error(f"Creation failed: {e}")
        print(f"Error: {e}")
        return

    # View events
    planner.view_events(upcoming=True)
    planner.view_events(upcoming=False)

    # Update an event
    planner.update_event(event1.event_id, description="Updated agenda", time="16:00")

    # View updated events
    planner.view_events(upcoming=True)

    # Delete an event
    planner.delete_event(event1.event_id)

    # View events after deletion
    planner.view_events(upcoming=True)

    # Test invalid date
    try:
        planner.create_event(
            name="Invalid Event",
            date="2025-07-01",
            time="25:00",
            location="Office",
            description="Test",
            attendees="Eve",
            reminder_set=False
        )
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()