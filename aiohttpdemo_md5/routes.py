from views import submit, check


def setup_routes(app):
    app.router.add_post('/submit', submit)
    app.router.add_get('/check', check)
