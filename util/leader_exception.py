class Error(Exception):
   """Base class for other exceptions"""
   pass
class LeaderException(Error):
   """Raised when the leader is changed"""
   pass