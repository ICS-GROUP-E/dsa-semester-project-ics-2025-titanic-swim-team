import datetime
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Event class
class Event:
    def __init__(self, event_id, name, date, time, reminder_set):
        self.event_id = event_id
        self.name = name
        self.date = date
        self.time = time
        self.reminder_set = reminder_set

    def __copy__(self):
        return Event(self.event_id, self.name, self.date, self.time, self.reminder_set)

# Event Planner class with queue functionality
class EventPlanner:
    def __init__(self):
        self.events = {}  # {event_id: Event}
        self.reminder_queue = []  # Queue for events with reminders
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

    def create_event(self, name, date, time, reminder_set):
        """Create a new event and enqueue if reminder is set."""
        logger.info(f"Creating event: {name}, {date} {time}")
        self._get_datetime(date, time)
        event = Event(self.event_id_counter, name, date, time, reminder_set)
        self.events[event.event_id] = event
        if reminder_set:
            self.reminder_queue.append(event)
        self.event_id_counter += 1
        logger.info(f"Event created: ID={event.event_id}")
        print(f"Created event: {event.name} (ID: {event.event_id}) on {event.date} at {event.time}")
        return event

    def process_reminders(self):
        """Process reminders from the queue based on current time."""
        current_time = datetime.datetime.now()
        processed = []
        for event in self.reminder_queue:
            event_time = self._get_datetime(event.date, event.time)
            if event_time <= current_time + datetime.timedelta(minutes=15):
                logger.info(f"Reminder: {event.name} at {event_time}")
                print(f"Reminder: {event.name} at {event.date} {event.time}")
                processed.append(event)
        for event in processed:
            self.reminder_queue.remove(event)
        logger.info(f"Processed {len(processed)} reminders, {len(self.reminder_queue)} remaining")
        print(f"Processed {len(processed)} reminders, {len(self.reminder_queue)} remaining")

    def view_reminder_queue(self):
        """View the current reminder queue."""
        logger.info(f"Viewing {len(self.reminder_queue)} reminders in queue")
        print(f"\nReminder Queue:")
        for event in self.reminder_queue:
            print(f"ID: {event.event_id}, Name: {event.name}, Date: {event.date}, Time: {event.time}")
        return self.reminder_queue.copy()

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
        event1 = planner.create_event("Team Meeting", "2025-07-10", "15:00", True)
        event2 = planner.create_event("Client Call", "2025-07-15", "10:00", False)
    except ValueError as e:
        print(f"Error: {e}")
        return

    # View events and reminders
    planner.view_events()
    planner.view_reminder_queue()

    # Process reminders
    planner.process_reminders()

    # View reminder queue after processing
    planner.view_reminder_queue()

    # Test invalid datetime
    try:
        planner.create_event("Invalid Event", "2025-07-01", "25:00", False)
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()