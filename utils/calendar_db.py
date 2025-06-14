"""
Calendar events database utilities for DuckDB.
Handles storage and retrieval of calendar events extracted from images.
"""

import duckdb
import os
from typing import List, Dict, Optional
from datetime import datetime
import streamlit as st
import logging

logger = logging.getLogger(__name__)

class CalendarEventDB:
    """Database operations for calendar events."""
    
    def __init__(self, db_path: str = None):
        """Initialize calendar events database."""
        self.db_path = db_path or os.getenv("USER_DB_PATH", "users.db")
        self.init_calendar_table()
    
    def init_calendar_table(self):
        """Initialize calendar events table if it doesn't exist."""
        conn = duckdb.connect(self.db_path)
        
        try:
            # Create calendar_events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS calendar_events (
                    id INTEGER PRIMARY KEY,
                    title VARCHAR NOT NULL,
                    event_date VARCHAR,
                    event_time VARCHAR,
                    location VARCHAR,
                    description TEXT,
                    extracted_text TEXT,
                    created_by VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            logger.info("Calendar events table initialized")
            
        except Exception as e:
            logger.error(f"Error initializing calendar events table: {str(e)}")
        finally:
            conn.close()
    
    def add_calendar_event(self, event: Dict[str, str], username: str, extracted_text: str = "") -> bool:
        """
        Add a calendar event to the database.
        
        Args:
            event: Dictionary containing event details
            username: User who created the event
            extracted_text: Original extracted text from image
            
        Returns:
            True if successful, False otherwise
        """
        conn = duckdb.connect(self.db_path)
        
        try:
            conn.execute("""
                INSERT INTO calendar_events 
                (title, event_date, event_time, location, description, extracted_text, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event.get("title", ""),
                event.get("date", ""),
                event.get("time", ""),
                event.get("location", ""),
                event.get("description", ""),
                extracted_text,
                username
            ))
            
            logger.info(f"Added calendar event: {event.get('title')}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding calendar event: {str(e)}")
            return False
        finally:
            conn.close()
    
    def get_all_calendar_events(self, username: str = None) -> List[Dict]:
        """
        Retrieve all calendar events, optionally filtered by user.
        
        Args:
            username: Filter events by this user (None for all events)
            
        Returns:
            List of calendar event dictionaries
        """
        conn = duckdb.connect(self.db_path)
        
        try:
            if username:
                query = """
                    SELECT id, title, event_date, event_time, location, description, 
                           created_by, created_at, updated_at
                    FROM calendar_events 
                    WHERE created_by = ? 
                    ORDER BY created_at DESC
                """
                results = conn.execute(query, (username,)).fetchall()
            else:
                query = """
                    SELECT id, title, event_date, event_time, location, description, 
                           created_by, created_at, updated_at
                    FROM calendar_events 
                    ORDER BY created_at DESC
                """
                results = conn.execute(query).fetchall()
            
            events = []
            for result in results:
                events.append({
                    "id": result[0],
                    "title": result[1],
                    "event_date": result[2],
                    "event_time": result[3],
                    "location": result[4],
                    "description": result[5],
                    "created_by": result[6],
                    "created_at": result[7],
                    "updated_at": result[8]
                })
            
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving calendar events: {str(e)}")
            return []
        finally:
            conn.close()
    
    def update_calendar_event(self, event_id: int, event: Dict[str, str]) -> bool:
        """
        Update a calendar event.
        
        Args:
            event_id: ID of the event to update
            event: Dictionary containing updated event details
            
        Returns:
            True if successful, False otherwise
        """
        conn = duckdb.connect(self.db_path)
        
        try:
            conn.execute("""
                UPDATE calendar_events 
                SET title = ?, event_date = ?, event_time = ?, location = ?, 
                    description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                event.get("title", ""),
                event.get("date", ""),
                event.get("time", ""),
                event.get("location", ""),
                event.get("description", ""),
                event_id
            ))
            
            logger.info(f"Updated calendar event ID: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating calendar event: {str(e)}")
            return False
        finally:
            conn.close()
    
    def delete_calendar_event(self, event_id: int) -> bool:
        """
        Delete a calendar event.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            True if successful, False otherwise
        """
        conn = duckdb.connect(self.db_path)
        
        try:
            conn.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
            logger.info(f"Deleted calendar event ID: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting calendar event: {str(e)}")
            return False
        finally:
            conn.close()
    
    def get_calendar_stats(self) -> Dict[str, int]:
        """
        Get calendar events statistics.
        
        Returns:
            Dictionary with various statistics
        """
        conn = duckdb.connect(self.db_path)
        
        try:
            # Total events
            total_events = conn.execute("SELECT COUNT(*) FROM calendar_events").fetchone()[0]
            
            # Events by user
            user_counts = conn.execute("""
                SELECT created_by, COUNT(*) as count 
                FROM calendar_events 
                GROUP BY created_by
            """).fetchall()
            
            # Recent events (last 7 days)
            recent_events = conn.execute("""
                SELECT COUNT(*) FROM calendar_events 
                WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL 7 DAY
            """).fetchone()[0]
            
            return {
                "total_events": total_events,
                "recent_events": recent_events,
                "user_counts": dict(user_counts) if user_counts else {}
            }
            
        except Exception as e:
            logger.error(f"Error getting calendar stats: {str(e)}")
            return {"total_events": 0, "recent_events": 0, "user_counts": {}}
        finally:
            conn.close()


@st.cache_resource
def get_calendar_db() -> CalendarEventDB:
    """Get cached calendar database instance."""
    return CalendarEventDB()
