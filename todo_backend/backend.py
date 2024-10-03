import os
from src import backend, db

if __name__ == '__main__':
    with backend.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5001))
    print(f'Backend server has started on port {port}...')
    backend.run(host='0.0.0.0', port=port, debug=True)