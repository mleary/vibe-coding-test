import streamlit as st
import pandas as pd
from utils.db_auth import get_user_db
from utils.login import is_admin
from utils.azure_ai import get_azure_openai_extractor, validate_azure_openai_configuration
from utils.calendar_db import get_calendar_db
from PIL import Image
import io

def calendar_events_page():
    """Calendar Events management page with AI-powered image extraction"""
    if not is_admin():
        st.error("🚫 Access denied. Admin privileges required.")
        return
    
    st.title("📅 Calendar Events Manager")
    
    # Check Azure configuration
    azure_config = validate_azure_openai_configuration()
    
    if not azure_config["configured"]:
        st.error("❌ Azure OpenAI not configured. Please check your environment variables.")
        st.code("""Required environment variables:
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview""")
        return
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs(["📷 Upload & Extract", "📅 Manage Events", "📊 Statistics"])
        
        with tab1:
            st.subheader("📷 Upload Calendar Image")
            uploaded_file = st.file_uploader(
                "Choose an image of a calendar, schedule, or event information...",
                type=['png', 'jpg', 'jpeg'],
                help="Upload a clear image containing calendar events, dates, times, and event details."
            )
            
            if uploaded_file is not None:
                # Display uploaded image
                image = Image.open(uploaded_file)
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.image(image, caption="Uploaded Image", use_column_width=True)
                    
                    # Image info
                    st.write(f"**Image size:** {image.size[0]} x {image.size[1]} pixels")
                    st.write(f"**File size:** {len(uploaded_file.getvalue())} bytes")
                
                with col2:
                    st.subheader("🤖 AI Analysis")
                    
                    if st.button("🔍 Extract Calendar Events", type="primary"):
                        with st.spinner("Analyzing image with Azure OpenAI GPT-4 Vision..."):
                            try:
                                # Get Azure OpenAI extractor
                                extractor = get_azure_openai_extractor()
                                
                                # Extract calendar events
                                events = extractor.extract_calendar_events_from_image(image)
                                
                                if events:
                                    st.success(f"✅ Found {len(events)} potential calendar events!")
                                    
                                    # Store extracted text in session state for saving later
                                    if hasattr(extractor, '_last_extracted_text'):
                                        st.session_state['last_extracted_text'] = extractor._last_extracted_text
                                    
                                    # Display events for review
                                    st.subheader("📋 Extracted Events")
                                    
                                    calendar_db = get_calendar_db()
                                    
                                    for i, event in enumerate(events):
                                        with st.expander(f"Event {i+1}: {event.get('title', 'Untitled')}", expanded=True):
                                            col_a, col_b = st.columns(2)
                                            
                                            with col_a:
                                                # Editable event details
                                                event_title = st.text_input(
                                                    "Title", 
                                                    value=event.get('title', ''),
                                                    key=f"title_{i}"
                                                )
                                                event_date = st.text_input(
                                                    "Date", 
                                                    value=event.get('date', ''),
                                                    key=f"date_{i}"
                                                )
                                                event_time = st.text_input(
                                                    "Time", 
                                                    value=event.get('time', ''),
                                                    key=f"time_{i}"
                                                )
                                            
                                            with col_b:
                                                event_location = st.text_input(
                                                    "Location", 
                                                    value=event.get('location', ''),
                                                    key=f"location_{i}"
                                                )
                                                event_description = st.text_area(
                                                    "Description", 
                                                    value=event.get('description', ''),
                                                    key=f"description_{i}",
                                                    height=100
                                                )
                                            
                                            # Save button for each event
                                            if st.button(f"💾 Save Event {i+1}", key=f"save_{i}"):
                                                event_data = {
                                                    "title": event_title,
                                                    "date": event_date,
                                                    "time": event_time,
                                                    "location": event_location,
                                                    "description": event_description
                                                }
                                                
                                                extracted_text = st.session_state.get('last_extracted_text', '')
                                                username = st.session_state.get('username', 'unknown')
                                                
                                                if calendar_db.add_calendar_event(event_data, username, extracted_text):
                                                    st.success(f"✅ Saved event: {event_title}")
                                                else:
                                                    st.error("❌ Failed to save event")
                                
                                else:
                                    st.warning("No calendar events detected in the image.")
                                    
                                    # Show extracted text for debugging
                                    if hasattr(extractor, 'get_last_response'):
                                        raw_response = extractor.get_last_response()
                                        if raw_response:
                                            with st.expander("🔍 Raw AI Response (for debugging)"):
                                                st.text_area("AI Response:", raw_response, height=200)
                            
                            except Exception as e:
                                st.error(f"❌ Error processing image: {str(e)}")
                                st.write("Please check your Azure OpenAI configuration and try again.")
        
        with tab2:
            st.subheader("📅 Saved Calendar Events")
            
            calendar_db = get_calendar_db()
            saved_events = calendar_db.get_all_calendar_events()
            
            if saved_events:
                # Create dataframe for display
                events_data = []
                for event in saved_events:
                    events_data.append({
                        "ID": event["id"],
                        "Title": event["title"],
                        "Date": event["event_date"],
                        "Time": event["event_time"], 
                        "Location": event["location"],
                        "Created By": event["created_by"],
                        "Created At": event["created_at"]
                    })
                
                df_events = pd.DataFrame(events_data)
                st.dataframe(df_events, use_container_width=True)
                
                # Event management
                st.subheader("🛠️ Manage Events")
                
                if saved_events:
                    selected_event_id = st.selectbox(
                        "Select event to manage:",
                        options=[e["id"] for e in saved_events],
                        format_func=lambda x: next(e["title"] for e in saved_events if e["id"] == x)
                    )
                    
                    col_manage1, col_manage2, col_manage3 = st.columns(3)
                    
                    with col_manage1:
                        if st.button("📝 Edit Event", key="edit_event"):
                            st.info("Edit functionality can be added here")
                    
                    with col_manage2:
                        if st.button("🗑️ Delete Event", key="delete_event", type="secondary"):
                            if calendar_db.delete_calendar_event(selected_event_id):
                                st.success("Event deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete event")
                    
                    with col_manage3:
                        if st.button("📋 View Details", key="view_details"):
                            selected_event = next(e for e in saved_events if e["id"] == selected_event_id)
                            with st.expander("Event Details", expanded=True):
                                st.write(f"**Title:** {selected_event['title']}")
                                st.write(f"**Date:** {selected_event['event_date']}")
                                st.write(f"**Time:** {selected_event['event_time']}")
                                st.write(f"**Location:** {selected_event['location']}")
                                st.write(f"**Description:** {selected_event['description']}")
                                st.write(f"**Created By:** {selected_event['created_by']}")
                                st.write(f"**Created At:** {selected_event['created_at']}")
                                if selected_event['extracted_text']:
                                    st.text_area("Original Extracted Text:", selected_event['extracted_text'], height=100)
            
            else:
                st.info("No calendar events saved yet. Upload an image in the 'Upload & Extract' tab to get started!")
        
        with tab3:
            st.subheader("📊 Calendar Events Statistics")
            
            calendar_db = get_calendar_db()
            stats = calendar_db.get_calendar_stats()
            
            # Main metrics
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.metric("Total Events", stats["total_events"])
            
            with col_stat2:
                st.metric("Recent Events (7 days)", stats["recent_events"])
            
            with col_stat3:
                if stats["user_counts"]:
                    most_active_user = max(stats["user_counts"].items(), key=lambda x: x[1])
                    st.metric("Most Active User", f"{most_active_user[0]} ({most_active_user[1]})")
                else:
                    st.metric("Most Active User", "None")
            
            # Detailed statistics
            if saved_events:
                st.divider()
                
                # User activity chart
                if stats["user_counts"]:
                    st.subheader("👥 Events by User")
                    user_df = pd.DataFrame(list(stats["user_counts"].items()), columns=["User", "Event Count"])
                    st.bar_chart(user_df.set_index("User"))
                
                # Recent activity timeline
                st.subheader("📅 Recent Activity")
                recent_events = sorted(saved_events, key=lambda x: x["created_at"], reverse=True)[:10]
                
                for event in recent_events:
                    st.write(f"📝 **{event['title']}** ({event['event_date']}) - Created by {event['created_by']} on {event['created_at']}")
            
            else:
                st.info("No events data available for statistics.")
