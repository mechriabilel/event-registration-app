import argparse
import json
import os
import sys

DATA_FILE = "events_data.json"

def load_data():
    """Load data from JSON file or return default structure if missing/corrupted."""
    if not os.path.exists(DATA_FILE):
        return {"events": [], "registrations": [], "next_event_id": 1, "next_reg_id": 1}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"events": [], "registrations": [], "next_event_id": 1, "next_reg_id": 1}

def save_data(data):
    """Save data dictionary to JSON file with indentation."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def handle_event(args, data):
    """Handle event-related commands: list, add, update, remove, search."""
    if args.event_action == "list":
        if not data["events"]:
            print("No events found.")
            return
        for e in data["events"]:
            regs = sum(1 for r in data["registrations"] if r["event_id"] == e["id"])
            print(f"ID: {e['id']} | Name: {e['name']} | Capacity: {e['capacity']} | Registered: {regs}")
            
    elif args.event_action == "add":
        event = {
            "id": data["next_event_id"],
            "name": args.name,
            "capacity": args.capacity
        }
        data["events"].append(event)
        data["next_event_id"] += 1
        save_data(data)
        print(f"Event '{args.name}' added with ID {event['id']}.")
        
    elif args.event_action == "update":
        event = next((e for e in data["events"] if e["id"] == args.id), None)
        if not event:
            print(f"Error: Event ID {args.id} not found.")
            return
        if args.name:
            event["name"] = args.name
        if args.capacity is not None:
            event["capacity"] = args.capacity
        save_data(data)
        print(f"Event ID {args.id} updated.")
        
    elif args.event_action == "remove":
        data["events"] = [e for e in data["events"] if e["id"] != args.id]
        data["registrations"] = [r for r in data["registrations"] if r["event_id"] != args.id]
        save_data(data)
        print(f"Event ID {args.id} and associated registrations removed.")
        
    elif args.event_action == "search":
        min_places = args.available_places
        results = []
        for e in data["events"]:
            regs = sum(1 for r in data["registrations"] if r["event_id"] == e["id"])
            available = e["capacity"] - regs
            if available >= min_places:
                results.append((e, available))
        if not results:
            print(f"No events found with at least {min_places} available places.")
        else:
            for e, avail in results:
                print(f"ID: {e['id']} | Name: {e['name']} | Available Places: {avail}/{e['capacity']}")

def handle_registration(args, data):
    """Handle registration-related commands: list, create, change, cancel."""
    if args.reg_action == "list":
        if not data["registrations"]:
            print("No registrations found.")
            return
        for r in data["registrations"]:
            print(f"Registration ID: {r['id']} | Event ID: {r['event_id']} | Attendee: {r['attendee']}")
            
    elif args.reg_action == "create":
        event = next((e for e in data["events"] if e["id"] == args.event), None)
        if not event:
            print(f"Error: Event ID {args.event} does not exist.")
            return
        
        current_regs = sum(1 for r in data["registrations"] if r["event_id"] == args.event)
        if current_regs >= event["capacity"]:
            print(f"Error: Cannot register. Event '{event['name']}' has reached max capacity ({event['capacity']}).")
            sys.exit(1)
            
        reg = {
            "id": data["next_reg_id"],
            "event_id": args.event,
            "attendee": args.attendee
        }
        data["registrations"].append(reg)
        data["next_reg_id"] += 1
        save_data(data)
        print(f"Registration successful! ID: {reg['id']} for {args.attendee}.")
        
    elif args.reg_action == "change":
        reg = next((r for r in data["registrations"] if r["id"] == args.id), None)
        if not reg:
            print(f"Error: Registration ID {args.id} not found.")
            return
        if args.attendee:
            reg["attendee"] = args.attendee
        save_data(data)
        print(f"Registration ID {args.id} updated.")
        
    elif args.reg_action == "cancel":
        data["registrations"] = [r for r in data["registrations"] if r["id"] != args.id]
        save_data(data)
        print(f"Registration ID {args.id} cancelled.")

def main():
    parser = argparse.ArgumentParser(description="Event Registration CLI App")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Event subparser
    event_parser = subparsers.add_parser("event", help="Manage events")
    event_sub = event_parser.add_subparsers(dest="event_action")
    
    event_sub.add_parser("list")
    
    add_e = event_sub.add_parser("add")
    add_e.add_argument("--name", required=True, type=str)
    add_e.add_argument("--capacity", required=True, type=int)
    
    up_e = event_sub.add_parser("update")
    up_e.add_argument("id", type=int)
    up_e.add_argument("--name", type=str)
    up_e.add_argument("--capacity", type=int)
    
    rm_e = event_sub.add_parser("remove")
    rm_e.add_argument("id", type=int)
    
    sr_e = event_sub.add_parser("search")
    sr_e.add_argument("--available-places", required=True, type=int)

    # Registration subparser
    reg_parser = subparsers.add_parser("registration", help="Manage registrations")
    reg_sub = reg_parser.add_subparsers(dest="reg_action")
    
    reg_sub.add_parser("list")
    
    create_r = reg_sub.add_parser("create")
    create_r.add_argument("--event", required=True, type=int)
    create_r.add_argument("--attendee", required=True, type=str)
    
    ch_r = reg_sub.add_parser("change")
    ch_r.add_argument("id", type=int)
    ch_r.add_argument("--attendee", type=str)
    
    cn_r = reg_sub.add_parser("cancel")
    cn_r.add_argument("id", type=int)

    args = parser.parse_args()
    data = load_data()

    if args.command == "event":
        handle_event(args, data)
    elif args.command == "registration":
        handle_registration(args, data)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()