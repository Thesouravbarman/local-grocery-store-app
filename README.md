# Apna Bazaar – Local Grocery Store Application

A responsive web app that connects a neighbourhood grocery store with its customers.
B.Tech CSE project, Coochbehar Government Engineering College (MAKAUT).

## Features
**Customer:** browse products, search, filter by category, see price and stock, basket with automatic totals, home delivery or store pickup with time slots, validated checkout, order status tracking.

**Store admin:** add/remove products, edit price and stock, low-stock alert (10 units or fewer), process orders through a status flow, cancel with automatic restock, customer records.

## Run
No installation. Open `index.html` in any modern browser.

## Tech
HTML, CSS and vanilla JavaScript in one file (about 14.6 KB). Data is saved in the browser's `localStorage`.

## Tests
32 automated test cases (Playwright + Chromium), all passing.
```bash
pip install playwright && playwright install chromium
python tests/test_app.py
```

## Screenshots
![Shop](screenshots/01_home.png)
![Admin](screenshots/07_admin_inv.png)

## Limitations
Prototype: data is stored per browser, no admin login, no SMS notifications. A server database, authentication and notifications are listed as future work in the report (`docs/Project_Report.pdf`).

## Author
Sourav – B.Tech Computer Science & Engineering

## License
MIT
