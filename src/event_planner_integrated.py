import datetime
import logging
from dataclasses import dataclass

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Event class
@dataclass
class Event:
    event_id: int
    name: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    reminder_set: bool
    location: str = ""
    description: str = ""
    attendees: str = ""  # Comma-separated names

    def __copy__(self):
        return Event(self.event_id, self.name, self.date, self.time, self.reminder_set, self.location, self.description, self.attendees)

# Node for Linked List (tasks)
class LLNode:
    def __init__(self, data: str, completed: bool = False):
        self.data = data
        self.completed = completed
        self.next = None

# Node for Binary Search Tree
class BSTNode:
    def __init__(self, event: Event):
        self.event = event
        self.left = None
        self.right = None

# Event Planner class integrating BST, Stack, Linked List, and Queue
class EventPlanner:
    def __init__(self):
        self.bst_root = None  # BST for events
        self.edit_stack = []  # Stack for recently edited events, max 10
        self.todo_lists = {}  # {event_id: LLNode} for tasks
        self.reminder_queue = []  # Queue for reminders
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

    def create_event(self, name, date, time, reminder_set, location="", description="", attendees=""):
        """Create a new event, insert into BST, and enqueue reminders."""
        logger.info(f"Creating event: {name}, {date} {time}")
        self._get_datetime(date, time)
        event = Event(self.event_id_counter, name, date, time, reminder_set, location, description, attendees)
        self._insert_bst(event)
        self.todo_lists[event.event_id] = None
        if reminder_set:
            self.reminder_queue.append(event)
        self.edit_stack.append(event)
        if len(self.edit_stack) > 10:
            self.edit_stack.pop(0)
        self.event_id_counter += 1
        logger.info(f"Event created: ID={event.event_id}")
        print(f"Created event: {event.name} (ID: {event.event_id}) on {event.date} at {event.time}")
        return event

    def _insert_bst(self, event):
        """Insert event into BST based on date and time."""
        logger.info(f"Inserting event {event.name} into BST")
        if not self.bst_root:
            self.bst_root = BSTNode(event)
        else:
            self._insert_bst_recursive(self.bst_root, event)

    def _insert_bst_recursive(self, node, event):
        event_dt = self._get_datetime(event.date, event.time)
        node_dt = self._get_datetime(node.event.date, node.event.time)
        if event_dt < node_dt:
            if node.left is None:
                node.left = BSTNode(event)
            else:
                self._insert_bst_recursive(node.left, event)
        else:
            if node.right is None:
                node.right = BSTNode(event)
            else:
                self._insert_bst_recursive(node.right, event)

    def update_event(self, event_id, name=None, date=None, time=None, location=None, description=None, attendees=None, reminder_set=None):
        """Update event details, reinsert into BST if date/time changes, and push old state to stack."""
        logger.info(f"Updating event ID={event_id}")
        event = self._find_event(self.bst_root, event_id)
        if not event:
            logger.info(f"Event {event_id} not found")
            print(f"Error: Event ID {event_id} not found")
            return None
        old_event = event.__copy__()
        if date or time:
            self._get_datetime(date or old_event.date, time or old_event.time)
        if name:
            event.name = name
        if date:
            event.date = date
        if time:
            event.time = time
        if location:
            event.location = location
        if description:
            event.description = description
        if attendees:
            event.attendees = attendees
        if reminder_set is not None:
            if reminder_set and not old_event.reminder_set:
                self.reminder_queue.append(event)
            elif not reminder_set and old_event.reminder_set:
                if event in self.reminder_queue:
                    self.reminder_queue.remove(event)
            event.reminder_set = reminder_set
        if date or time:
            self._delete_bst_node(self.bst_root, event_id)
            self._insert_bst(event)
        self.edit_stack.append(old_event)
        if len(self.edit_stack) > 10:
            self.edit_stack.pop(0)
        logger.info(f"Event {event_id} updated")
        print(f"Updated event: {event.name} (ID: {event_id})")
        return event

    def _find_event(self, node, event_id):
        """Find event by ID in BST."""
        if not node:
            return None
        if node.event.event_id == event_id:
            return node.event
        left = self._find_event(node.left, event_id)
        if left:
            return left
        return self._find_event(node.right, event_id)

    def _delete_bst_node(self, node, event_id):
        """Delete event from BST."""
        if not node:
            return None
        if node.event.event_id == event_id:
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

    def _find_min(self, node):
        """Find minimum node in BST."""
        current = node
        while current.left:
            current = current.left
        return current

    def delete_event(self, event_id):
        """Delete an event from BST and related data structures."""
        logger.info(f"Deleting event ID={event_id}")
        event = self._find_event(self.bst_root, event_id)
        if not event:
            logger.info(f"Event {event_id} not found")
            print(f"Error: Event ID {event_id} not found")
            return False
        self.bst_root = self._delete_bst_node(self.bst_root, event_id)
        self.todo_lists.pop(event_id, None)
        if event in self.reminder_queue:
            self.reminder_queue.remove(event)
        logger.info(f"Event {event_id} deleted")
        print(f"Deleted event: {event.name} (ID: {event_id})")
        return True

    def view_events(self, upcoming=True):
        """View events in chronological order with upcoming/past filter."""
        current_date = datetime.datetime.now()
        events = []
        self._inorder_traversal(self.bst_root, events, current_date, upcoming)
        logger.info(f"Viewing {'upcoming' if upcoming else 'past'} events: {len(events)}")
        print(f"\n{'Upcoming' if upcoming else 'Past'} Events:")
        for event in events:
            print(f"ID: {event.event_id}, Name: {event.name}, Date: {event.date}, Time: {event.time}, Location: {event.location}")
        return events

    def _inorder_traversal(self, node, events, current_date, upcoming):
        """In-order traversal of BST with date filter."""
        if node:
            self._inorder_traversal(node.left, events, current_date, upcoming)
            event_dt = self._get_datetime(node.event.date, node.event.time)
            if (upcoming and event_dt >= current_date) or (not upcoming and event_dt < current_date):
                events.append(node.event)
            self._inorder_traversal(node.right, events, current_date, upcoming)

    def add_task(self, event_id, task):
        """Add a task to an event's to-do list."""
        logger.info(f"Adding task '{task}' to event {event_id}")
        if event_id not in [e.event_id for e in self.view_events()]:
            logger.info(f"Event {event_id} not found")
            print(f"Error: Event ID {event_id} not found")
            return False
        new_node = LLNode(task)
        if self.todo_lists.get(event_id) is None:
            self.todo_lists[event_id] = new_node
        else:
            current = self.todo_lists[event_id]
            while current.next:
                current = current.next
            current.next = new_node
        logger.info(f"Task '{task}' added")
        print(f"Added task '{task}' to event ID {event_id}")
        return True

    def remove_task(self, event_id, task):
        """Remove a task from an event's to-do list."""
        logger.info(f"Removing task '{task}' from event {event_id}")
        if event_id not in [e.event_id for e in self.view_events()] or self.todo_lists.get(event_id) is None:
            logger.info(f"Event {event_id} or task list not found")
            print(f"Error: Event ID {event_id} or task list not found")
            return False
        current = self.todo_lists[event_id]
        if current.data == task:
            self.todo_lists[event_id] = current.next
            logger.info(f"Task '{task}' removed")
            print(f"Removed task '{task}' from event ID {event_id}")
            return True
        while current.next:
            if current.next.data == task:
                current.next = current.next.next
                logger.info(f"Task '{task}' removed")
                print(f"Removed task '{task}' from event ID {event_id}")
                return True
            current = current.next
        logger.info(f"Task '{task}' not found")
        print(f"Error: Task '{task}' not found for event ID {event_id}")
        return False

    def mark_task_complete(self, event_id, task):
        """Mark a task as complete."""
        logger.info(f"Marking task '{task}' complete for event {event_id}")
        if event_id not in [e.event_id for e in self.view_events()] or self.todo_lists.get(event_id) is None:
            logger.info(f"Event {event_id} or task list not found")
            print(f"Error: Event ID {event_id} or task list not found")
            return False
        current = self.todo_lists[event_id]
        while current:
            if current.data == task:
                current.completed = True
                logger.info(f"Task '{task}' marked complete")
                print(f"Marked task '{task}' as complete for event ID {event_id}")
                return True
            current = current.next
        logger.info(f"Task '{task}' not found")
        print(f"Error: Task '{task}' not found for event ID {event_id}")
        return False

    def get_tasks(self, event_id):
        """Get tasks for an event with completion status."""
        logger.info(f"Getting tasks for event {event_id}")
        if event_id not in [e.event_id for e in self.view_events()] or self.todo_lists.get(event_id) is None:
            logger.info(f"Event {event_id} or task list not found")
            print(f"Error: Event ID {event_id} or task list not found")
            return []
        tasks = []
        current = self.todo_lists[event_id]
        while current:
            tasks.append({"task": current.data, "completed": current.completed})
            current = current.next
        logger.info(f"Retrieved {len(tasks)} tasks")
        print(f"\nTasks for event ID {event_id}:")
        for task in tasks:
            print(f"[{'x' if task['completed'] else ' '}] {task['task']}")
        return tasks

    def undo_last_edit(self):
        """Undo the last edit by popping from stack and restoring."""
        logger.info("Undoing last edit")
        if not self.edit_stack:
            logger.info("No edits to undo")
            print("Error: No edits to undo")
            return None
        last_event = self.edit_stack.pop()
        if last_event.event_id in [e.event_id for e in self.view_events()]:
            self._delete_bst_node(self.bst_root, last_event.event_id)
            self._insert_bst(last_event)
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

def main():
    """Demonstrate EventPlanner functionality."""
    planner = EventPlanner()
    
    # Create sample events
    event1 = planner.create_event(
        name="Team Meeting",
        date="2025-07-10",
        time="15:00",
        reminder_set=True,
        location="Office",
        description="Discuss project",
        attendees="Alice,Bob"
    )
    event2 = planner.create_event(
        name="Client Call",
        date="2025-07-15",
        time="10:00",
        reminder_set=False,
        location="Online",
        description="Review progress",
        attendees="Charlie"
    )

    # Add tasks
    planner.add_task(event1.event_id, "Prepare slides")
    planner.add_task(event1.event_id, "Send invites")
    planner.mark_task_complete(event1.event_id, "Prepare slides")

    # View events and tasks
    planner.view_events(upcoming=True)
    planner.get_tasks(event1.event_id)
    planner.view_reminder_queue()

    # Update an event
    planner.update_event(event1.event_id, name="Updated Meeting", time="16:00")

    # View updated events and edited stack
    planner.view_events(upcoming=True)
    planner.view_edited_events()

    # Process reminders
    planner.process_reminders()

    # Undo last edit
    planner.undo_last_edit()

    # View final state
    planner.view_events(upcoming=True)
    planner.view_edited_events()

    # Test invalid datetime
    try:
        planner.create_event(
            name="Invalid Event",
            date="2025-07-01",
            time="25:00",
            reminder_set=False
        )
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()