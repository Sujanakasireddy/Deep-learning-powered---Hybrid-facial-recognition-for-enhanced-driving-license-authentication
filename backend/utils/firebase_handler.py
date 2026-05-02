"""
Firebase handler - OPTIONAL
Since we're using SQLite for the freelance project,
this file is kept for compatibility but not used.
You can delete this file if not needed.
"""

class FirebaseHandler:
    """Placeholder for Firebase integration (not used in SQLite version)"""
    
    def __init__(self):
        print("⚠️ FirebaseHandler: SQLite is used instead of Firebase")
        pass
    
    def store_data(self, collection, doc_id, data):
        """Placeholder method"""
        raise NotImplementedError("Using SQLite database instead")
    
    def get_data(self, collection, doc_id):
        """Placeholder method"""
        raise NotImplementedError("Using SQLite database instead")
