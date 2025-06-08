import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, timedelta, date
import io

def generate_dummy_events():
    """Generate some dummy events for the calendar"""
    today = datetime.now()
    events = [
        {
            "title": "Team Meeting",
            "start": today.strftime("%Y-%m-%d") + "T10:00:00",
            "end": today.strftime("%Y-%m-%d") + "T11:00:00",
            "resourceId": "a",
            "backgroundColor": "#FF6B6B",
            "borderColor": "#FF6B6B"
        },
        {
            "title": "Project Review",
            "start": (today + timedelta(days=1)).strftime("%Y-%m-%d") + "T14:00:00",
            "end": (today + timedelta(days=1)).strftime("%Y-%m-%d") + "T15:30:00",
            "resourceId": "b",
            "backgroundColor": "#4ECDC4",
            "borderColor": "#4ECDC4"
        },
        {
            "title": "Client Call",
            "start": (today + timedelta(days=3)).strftime("%Y-%m-%d") + "T09:00:00",
            "end": (today + timedelta(days=3)).strftime("%Y-%m-%d") + "T10:00:00",
            "resourceId": "c",
            "backgroundColor": "#45B7D1",
            "borderColor": "#45B7D1"
        },
        {
            "title": "Workshop",
            "start": (today + timedelta(days=7)).strftime("%Y-%m-%d") + "T13:00:00",
            "end": (today + timedelta(days=7)).strftime("%Y-%m-%d") + "T17:00:00",
            "resourceId": "d",
            "backgroundColor": "#FFA07A",
            "borderColor": "#FFA07A"
        },
        {
            "title": "Code Review",
            "start": (today - timedelta(days=2)).strftime("%Y-%m-%d") + "T11:00:00",
            "end": (today - timedelta(days=2)).strftime("%Y-%m-%d") + "T12:00:00",
            "resourceId": "e",
            "backgroundColor": "#98D8C8",
            "borderColor": "#98D8C8"
        }
    ]
    return events

def create_ics_content(events):
    """Create ICS file content from events"""
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//My Streamlit App//Calendar//EN\n"
    
    for event in events:
        # Parse the datetime
        start_dt = datetime.fromisoformat(event["start"])
        end_dt = datetime.fromisoformat(event["end"])
        
        # Format for ICS (YYYYMMDDTHHMMSS)
        start_ics = start_dt.strftime("%Y%m%dT%H%M%S")
        end_ics = end_dt.strftime("%Y%m%dT%H%M%S")
        
        ics_content += f"""BEGIN:VEVENT
DTSTART:{start_ics}
DTEND:{end_ics}
SUMMARY:{event["title"]}
UID:{event["title"].replace(" ", "_").lower()}_{start_ics}@mystreamlitapp.com
END:VEVENT
"""
    
    ics_content += "END:VCALENDAR"
    return ics_content

def calendar_page():
    st.title("📅 Calendar")
    
    # Generate dummy events
    events = generate_dummy_events()
    
    # Calendar configuration
    calendar_options = {
        "editable": "true",
        "navLinks": "true",
        "selectable": "true",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay"
        },
        "initialView": "dayGridMonth",
        "height": 650,
        "themeSystem": "standard"
    }
    
    # Custom CSS for clean styling
    calendar_css = """
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-weight: bold;
    }
    .fc-event-title {
        font-weight: normal;
    }
    """
    
    # Display the calendar
    with st.container():
        calendar_component = calendar(
            events=events,
            options=calendar_options,
            custom_css=calendar_css,
            key="calendar"
        )
    
    # Show event details if an event is clicked
    if calendar_component.get("eventClick"):
        st.subheader("📋 Event Details")
        event_data = calendar_component["eventClick"]["event"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Title:** {event_data['title']}")
            st.write(f"**Start:** {event_data['start']}")
        with col2:
            st.write(f"**End:** {event_data['end']}")
            if 'extendedProps' in event_data:
                st.write(f"**Resource:** {event_data.get('resourceId', 'N/A')}")
    
    # Download section
    st.divider()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.subheader("📥 Export Calendar")
        
        # Create ICS content
        ics_content = create_ics_content(events)
        
        # Download button
        st.download_button(
            label="📅 Download Calendar (.ics)",
            data=ics_content,
            file_name=f"calendar_export_{datetime.now().strftime('%Y%m%d')}.ics",
            mime="text/calendar",
            help="Download your calendar events as an ICS file to import into other calendar applications",
            use_container_width=True
        )
    
    # Quick stats
    with st.expander("📊 Calendar Stats"):
        today = datetime.now().date()
        upcoming_events = [e for e in events if datetime.fromisoformat(e["start"]).date() >= today]
        past_events = [e for e in events if datetime.fromisoformat(e["start"]).date() < today]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Events", len(events))
        with col2:
            st.metric("Upcoming", len(upcoming_events))
        with col3:
            st.metric("Past", len(past_events))

if __name__ == "__main__":
    calendar_page()