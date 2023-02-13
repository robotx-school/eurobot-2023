import requests

data = [
    {
        "action": -1,
        "start_point": [
            0,
            356
        ],
        "direction": "E"
    },
    {
        "action": 1,
        "point": [
            200,
            356
        ]
    }

]


r = requests.post('http://192.168.0.188:8080/api/update_route', json=data)

print(r)
print(r.text)
