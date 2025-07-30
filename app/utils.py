import fastf1

def get_session(year, rnd, session_type):
    session = fastf1.get_session(year, rnd, session_type.upper())
    session.load()
    return session
