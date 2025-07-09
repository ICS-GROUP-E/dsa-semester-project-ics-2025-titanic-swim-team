import datetime
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Event class
class Event:
    def __init__(self, event_id, name, date, time):
        self.event_id = event_id
        self.name = name
        self.date = date
        self.time = time

    def __copy__(self):
        return Event(self.event_id, self.name, self.date, self.time)

# Event Planner class with stack functionality
class EventPlanner:
    def __init__(self):
        self.events = {}  # {event_id: Event}
        self.edit_stack = []  # Stack for recently edited events, max 10
        self.event_id_counter = 1
        logger.info("EventPlanner initialized")
        print("EventPlanner initialized")

    def _get_datetime(self, date, time):
        """Parse date/time."""
        try:
            dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            return dt
        except ValueError:
            logger.error(f"Invalid date/time format: {date} {time}")
            raise ValueError("Use YYYY-MM-DD HH:MM")

    def create_event(self, name, date, time):
        """Create a new event and push to stack."""
        logger.info(f"Creating event: {name}, {date} {time}")
        self._get_datetime(date, time)
        event = Event(self.event_id_counter, name, date, time)
        self.events[event.event_id] = event
        self.edit_stack.append(event)
        if len(self.edit_stack) > 10:
            self.edit_stack.pop(0)
        self.event_id_counter += 1
        logger.info(f"Event created: ID={event.event_id}")
        print(f"Created event: {event.name} (ID: {event.event_id}) on {event.date} at {event.time}")
        return event

    def update_event(self, event_id, name=None, date=None, time=None):
        """Update event details and push old state to stack."""
        logger.info(f"Updating event ID={event_id}")
        if event_id not in self.events:
            logger.info(f"Event {event_id} not found")
            print(f"Error: Event ID {event_id} not found")
            return None
        old_event = self.events[event_id].__copy__()
        if date or time:
            self._get_datetime(date or old_event.date, time or old_event.time)
        if name:
            self.events[event_id].name = name
        if date:
            self.events[event_id].date = date
        if time:
            self.events[event_id].time = time
        self.edit_stack.append(old_event)
        if len(self.edit_stack) > 10:
            self.edit_stack.pop(0)
        logger.info(f"Event {event_id} updated")
        print(f"Updated event: {self.events[event_id].name} (ID: {event_id})")
        return self.events[event_id]

    def undo_last_edit(self):
        """Undo the last edit by popping from stack and restoring."""
        logger.info("Undoing last edit")
        if not self.edit_stack:
            logger.info("No edits to undo")
            print("Error: No edits to undo")
            return None
        last_event = self.edit_stack.pop()
        if last_event.event_id in self.events:
            self.events[last_event.event_id] = last_event
            logger.info(f"Restored event ID={last_event.event_id}")
            print(f"Restored event: {last_event.name} (ID: {last_event.event_id})")
            return last_event
        logger.info(f"Event ID={last_event.event_id} not found")
        print(f"Error: Event ID {last_event.event_id} not found")
        return None

    def view_edited_events(self):
        """View the stack of recently edited events."""
        logger.info(f"Viewing {len(self.edit_stack)} edited events")
        print(f"\nRecently Edited Events:")
        for event in self.edit_stack:
            print(f"ID: {event.event_id}, Name: {event.name}, Date: {event.date}, Time: {event.time}")
        return self.edit_stack.copy()

    def view_events(self):
        """View all events."""
        logger.info(f"Viewing {len(self.events)} events")
        print(f"\nAll Events:")
        for event_id, event in self.events.items():
            print(f"ID: {event_id}, Name: {event.name}, Date: {event.date}, Time: {event.time}")
        return list(self.events.values())

def main():
    """Demonstrate EventPlanner functionality."""
    planner = EventPlanner()
    
    # Create sample events
    try:
        event1 = planner.create_event("Team Meeting", "2025-07-10", "15:00")
        event2 = planner.create_event("Client Call", "2025-07-15", "10:00")
    except ValueError as e:
        print(f"Error: {e}")
        return

    # View events
    planner.view_events()

    # Update an event
    planner.update_event(event1.event_id, name="Updated Meeting", time="16:00")

    # View updated events and edited stack
    planner.view_events()
    planner.view_edited_events()

    # Undo last edit
    planner.undo_last_edit()

    # View final state
    planner.view_events()
    planner.view_edited_events()

    # Test invalid datetime
    try:
        planner.create_event("Invalid Event", "2025-07-01", "25:00")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()