# Testing Progress — Shop

## Current Status
- Date: YYYY-MM-DD
- Total coverage: XX%
- Goal: 80%+

## Covered
- [x] `auth.py`
  - [x] login success
  - [x] login fail (401)
  - [x] `/auth/me` without token (401)
  - [x] `/auth/me` with token (200)

- [x] `customer.py`
  - [x] existing tests passing

- [x] `order.py`
  - [x] create order success (stock decreases, snapshot price)
  - [x] create order fail (not enough stock)
  - [x] update order item decrease success
  - [x] update order item fail (not enough stock)
  - [x] delete order success (stock returns)
  - [x] delete order not found (404)
  - [x] delete order item success (stock returns)
  - [x] delete order item not found (404)
  - [x] add item success
  - [x] add item fail (not enough stock)

## In Progress / Next
- [ ] `item.py` tests
  - [ ] show items success
  - [ ] add item success (upload + db record)
  - [ ] delete item success
  - [ ] delete item not found (404)

## Notes
- Use `client.request("DELETE", ..., json=...)` for DELETE with body.
- Keep integration style (API + DB), avoid heavy mocking.
- Clean dependency overrides after each test.

## Useful Commands
- Run tests: `./env/bin/python -m pytest`
- Coverage: `./env/bin/python -m pytest --cov=app --cov-report=term-missing`
