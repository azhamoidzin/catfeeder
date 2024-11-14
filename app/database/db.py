fake_users_db = {
    "johndoe@example.com": {
        'user_id': 0,
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2a$10$KSEpyXKj/a0KuV/z8eutQOpE9J6juwowmJO83fUzUp.u3oFdFP8GK",
        "disabled": False,
        "family_id": 0,
        'registration_date': '1970-01-01',

    },
    'vasia@example.com': {
        'user_id': 1,
        "full_name": "Vasia Piatkin",
        "email": "vasia@example.com",
        "hashed_password": "$2a$10$KSEpyXKj/a0KuV/z8eutQOpE9J6juwowmJO83fUzUp.u3oFdFP8GK",
        "disabled": False,
        "family_id": 0,
        'registration_date': '2024-01-01',
    }
}

fake_feeders_db = {
    'johndoe@example.com': {
        228: {
            'feeder_id': 228,
            'name': 'Kitchen',
            'tags': ['tag1'],
            'status': 0.5,
            'schedule': ['09:00', '12:00', '15:00', '18:00', '21:00'],
            'meal': 25
        },
        337: {
            'feeder_id': 337,
            'name': 'MainCoon OGROMNYI',
            'tags': ['tag3', 'tag5'],
            'status': 0.0,
            'schedule': ['09:30', '12:30', '15:30', '18:30', '18:41', '21:30'],
            'meal': 1000
        }
    }
}

fake_families_db = {
    0: {
        'id': 0,
        'name': 'SUPER FAMILY',
        'admin': 0,
    }
}

logs = []
