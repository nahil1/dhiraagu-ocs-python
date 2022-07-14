```python
import ocs
session = ocs.requests.session()
login_response, service_numbers, instance = ocs.login(session, '<email>', '<password>')
print(session.cookies)
for n in service_numbers:
  service_response, details = ocs.service_details(session, instance, n)
  print(details)
```
