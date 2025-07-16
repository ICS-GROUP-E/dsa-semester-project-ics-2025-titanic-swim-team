import datetime
import logging
from typing import Optional, List
from dataclasses import dataclass

# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Event class for event details
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

# Node for Linked List (tasks or attendees)
class LLNode:
    def __init__(self, data: str, completed: bool = False):
        self.data = data
        self.completed = completed  # For tasks only
        self.next = None

# Event Planner class with linked list functionality
class EventPlanner:
    def __init__(self):
        self.events = {}  # {event_id: Event}
        self.event_id_counter = 1
        self.todo_lists = {}  # {event_id: LLNode} for tasks
        self.attendees_lists = {}  # {event_id: LLNode} for attendees
        logger.info("EventPlanner initialized")

    def _get_datetime(self, date: str, time: str) -> datetime.datetime:
        """Parse and validate date/time."""
        try:
            dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            logger.debug(f"Parsed datetime: {date} {time} -> {dt}")
            return dt
        except ValueError:
            logger.error(f"Invalid date/time format: {date} {time}")
            raise ValueError("Invalid date or time format. Use YYYY-MM-DD and HH:MM.")

    def create_event(self, name: str, date: str, time: str, location: str, description: str, attendees: str, reminder_set: bool) -> Event:
        """Create a new event."""
        logger.info(f"Creating event: {name}, {date} {time}")
        self._get_datetime(date, time)  # Validate
        event = Event(self.event_id_counter, name, date, time, location, description, attendees, reminder_set)
        self.events[event.event_id] = event
        self.todo_lists[event.event_id] = None
        self.attendees_lists[event.event_id] = None
        self.event_id_counter += 1
        logger.info(f"Event created: ID={event.event_id}")
        print(f"Created event: {event.name} (ID: {event.event_id}) on {event.date} at {event.time}")
        return event

    def update_event(self, event_id: int, **kwargs) -> Optional[Event]:
        """Update event details."""
        logger.info(f"Updating event ID={event_id}: {kwargs}")
        if event_id not in self.events:
            logger.warning(f"Event {event_id} not found for update")
            print(f"Error: Event ID {event_id} not found")
            return None
        event = self.events[event_id]
        if "date" in kwargs or "time" in kwargs:
            new_date = kwargs.get("date", event.date)
            new_time = kwargs.get("time", event.time)
            self._get_datetime(new_date, new_time)
        for key, value in kwargs.items():
            if hasattr(event, key):
                setattr(event, key, value)
        logger.info(f"Event {event_id} updated")
        print(f"Updated event: {event.name} (ID: {event_id})")
        return event

    def delete_event(self, event_id: int) -> bool:
        """Delete an event and its linked lists."""
        logger.info(f"Deleting event ID={event_id}")
        if event_id not in self.events:
            logger.warning(f"Event {event_id} not found for deletion")
            print(f"Error: Event ID {event_id} not found")
            return False
        event_name = self.events[event_id].name
        del self.events[event_id]
        self.todo_lists.pop(event_id, None)
        self.attendees_lists.pop(event_id, None)
        logger.info(f"Event {event_id} deleted")
        print(f"Deleted event: {event_name} (ID: {event_id})")
        return True

    def view_events(self, upcoming: bool = True) -> List[Event]:
        """View upcoming or past events."""
        current_date = datetime.datetime.now()
        events = []
        for event in self.events.values():
            event_dt = self._get_datetime(event.date, event.time)
            if (upcoming and event_dt >= current_date) or (not upcoming and event_dt < current_date):
                events.append(event)
        logger.info(f"Viewing {'upcoming' if upcoming else 'past'} events: {len(events)} found")
        print(f"\n{'Upcoming' if upcoming else 'Past'} Events:")
        for event in events:
            print(f"ID: {event.event_id}, Name: {event.name}, Date: {event.date}, Time: {event.time}, Location: {event.location}")
        return events

    def add_task(self, event_id: int, task: str) -> bool:
        """Add a task to an event."""
        logger.info(f"Adding task to event ID={event_id}: {task}")
        if event_id not in self.events:
            logger.warning(f"Event {event_id} not found for adding task")
            print(f"Error: Event ID {event_id} not found")
            return False
        new_node = LLNode(task)
        if not self.todo_lists[event_id]:
            self.todo_lists[event_id] = new_node
        else:
            current = self.todo_lists[event_id]
            while current.next:
                current = current.next
            current.next = new_node
        logger.info(f"Task added to event {event_id}: {task}")
        print(f"Added task '{task}' to event ID {event_id}")
        return True

    def view_tasks(self, event_id: int) -> List[str]:
        """View tasks for an event."""
        logger.info(f"Viewing tasks for event ID={event_id}")
        if event_id not in self.events:
            logger.warning(f"Event {event_id} not found for viewing tasks")
            print(f"Error: Event ID {event_id} not found")
            return []
        tasks = []
        current = self.todo_lists[event_id]
        while current:
            tasks.append(f"{'[x]' if current.completed else '[ ]'} {current.data}")
            current = current.next
        print(f"\nTasks for event ID {event_id}:")
        for task in tasks:
            print(task)
        return tasks

def main():
    """Demonstrate EventPlanner functionality."""
    planner = EventPlanner()
    
    # Create sample events
    planner.create_event(
        name="Team Meeting",
        date="2025-07-10",
        time="14:00",
        location="Conference Room A",
        description="Weekly team sync",
        attendees="Alice,Bob,Charlie",
        reminder_set=True
    )
    
    planner.create_event(
        name="Company Picnic",
        date="2025-07-15",
        time="12:00",
        location="Central Park",
        description="Annual company outing",
        attendees="All employees",
        reminder_set=False
    )
    
    # Add tasks to events
    planner.add_task(1, "Prepare agenda")
    planner.add_task(1, "Book projector")
    planner.add_task(2, "Order catering")
    
    # View events and tasks
    planner.view_events(upcoming=True)
    planner.view_tasks(1)
    planner.view_tasks(2)
    
    # Update an event
    planner.update_event(1, time="15:00", location="Conference Room B")
    
    # View updated events
    planner.view_events(upcoming=True)
    
    # Delete an event
    planner.delete_event(2)
    
    # View final events
    planner.view_events(upcoming=True)

if __name__ == "__main__":
    main()