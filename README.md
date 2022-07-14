```python
import ocs
session = ocs.requests.session()
login_response, service_numbers, instance = ocs.login(session, '<email>', '<password>')
print(session.cookies)
service_response, details = ocs.service_details(session, instance, service_numbers[0])
print(details)
```
