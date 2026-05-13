import fastf1

def get_session(year, rnd, session_type):
    session = fastf1.get_session(year, rnd, session_type.upper())
    session.load(
        laps=True,
        telemetry=True,
        weather=True,
        messages=False,
        livedata=None
    )
    return session