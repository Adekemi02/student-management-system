from api import create_app
from api.config.config import config


app = create_app(config=config['prod'])

if __name__ == '__main__':
    app.run()

