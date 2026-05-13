from app import app

def test_app_initializes():
    import dash
    assert isinstance(app, dash.Dash)

def test_layout_renders():
    assert app.layout is not None

def test_title():
    assert app.title is not None and app.title != ""