from django.test import TestCase

# Create your tests here.

for _ in range(1000):
    a = uuid.uuid4()
    print(urlsafe_b64encode(a.bytes).decode().replace('=', ''))
